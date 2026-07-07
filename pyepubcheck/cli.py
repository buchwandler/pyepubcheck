"""Command-line entrypoint."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path

from pyepubcheck import __version__
from pyepubcheck.api import validate_path
from pyepubcheck.config import ValidationConfig
from pyepubcheck.inspect import inspect_metadata, inspect_path
from pyepubcheck.io.expanded import DirectorySource
from pyepubcheck.messages import (
    apply_custom_message_overrides,
    load_custom_message_overrides,
)
from pyepubcheck.registry import SUPPORTED_MODES, SUPPORTED_PROFILES
from pyepubcheck.reports.console import render_console
from pyepubcheck.reports.inspection_console import (
    render_images_text,
    render_inspection_text,
    render_manifest_text,
    render_metadata_text,
    render_navigation_text,
    render_publication_summary,
    render_stats_text,
)
from pyepubcheck.reports.inspection_csv import render_images_csv, render_manifest_csv
from pyepubcheck.reports.inspection_json import inspection_report_to_data
from pyepubcheck.reports.inspection_markdown import render_inspection_markdown
from pyepubcheck.reports.json_report import render_json_report
from pyepubcheck.reports.xml_report import render_xml_report
from pyepubcheck.reports.xmp_report import render_xmp_report
from pyepubcheck.severity import Severity

KNOWN_COMMANDS = {"check", "inspect", "images", "metadata", "manifest", "nav", "stats"}


def build_legacy_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pyepubcheck", add_help=False)
    _add_help_and_version_arguments(parser)
    _add_check_arguments(parser, legacy=True)
    return parser


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pyepubcheck")
    parser.add_argument("--version", "-version", action="store_true", help="show version and exit")
    subparsers = parser.add_subparsers(dest="command")

    add_check_parser(subparsers)
    add_inspect_parser(subparsers)
    add_images_parser(subparsers)
    add_metadata_parser(subparsers)
    add_manifest_parser(subparsers)
    add_nav_parser(subparsers)
    add_stats_parser(subparsers)
    return parser


def add_check_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("check", help="validate a publication and optionally print a summary")
    _add_check_arguments(parser, legacy=False)


def add_inspect_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("inspect", help="inspect a publication")
    parser.add_argument("path", help="packaged EPUB or expanded EPUB directory")
    parser.add_argument(
        "--include",
        default="images,metadata,manifest,nav,stats,container",
        help="comma-separated sections",
    )
    parser.add_argument("--format", choices=("text", "json", "markdown"), default="text")
    parser.add_argument("--output", help="write inspection output to a file")
    parser.add_argument("--validate", action="store_true", help="include validation status")
    parser.add_argument("--estimate-pages", action="store_true", help="estimate pages from word count")
    parser.add_argument("--words-per-page", type=int, default=250, help="words-per-page divisor for page estimates")
    parser.add_argument("--limit", type=int, help="limit long list sections")
    parser.add_argument("--sort", choices=("path", "size", "type"), default="path")


def add_images_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("images", help="inspect publication images")
    parser.add_argument("path", help="packaged EPUB or expanded EPUB directory")
    parser.add_argument("--format", choices=("text", "json", "csv", "markdown"), default="text")
    parser.add_argument("--output", help="write image output to a file")
    parser.add_argument("--min-width", type=int)
    parser.add_argument("--min-height", type=int)
    parser.add_argument("--max-width", type=int)
    parser.add_argument("--max-height", type=int)
    parser.add_argument("--max-bytes", type=int)
    parser.add_argument("--image-format", choices=("jpeg", "png", "gif", "svg", "webp", "avif", "unknown"))
    parser.add_argument("--sort", choices=("path", "size", "width", "height", "pixels", "format"), default="path")
    parser.add_argument("--largest", type=int)
    parser.add_argument("--referenced-only", action="store_true")
    parser.add_argument("--unreferenced-only", action="store_true")
    parser.add_argument("--cover-only", action="store_true")


def add_metadata_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("metadata", help="inspect package metadata")
    parser.add_argument("path", help="packaged EPUB or expanded EPUB directory")
    parser.add_argument("--format", choices=("text", "json", "markdown"), default="text")
    parser.add_argument("--output", help="write metadata output to a file")


def add_manifest_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("manifest", help="inspect package manifest assets")
    parser.add_argument("path", help="packaged EPUB or expanded EPUB directory")
    parser.add_argument("--format", choices=("text", "json", "csv", "markdown"), default="text")
    parser.add_argument("--output", help="write manifest output to a file")
    parser.add_argument("--sort", choices=("path", "size", "type"), default="path")


def add_nav_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("nav", help="inspect EPUB navigation")
    parser.add_argument("path", help="packaged EPUB or expanded EPUB directory")
    parser.add_argument("--format", choices=("text", "json", "markdown"), default="text")
    parser.add_argument("--output", help="write navigation output to a file")


def add_stats_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("stats", help="inspect text statistics")
    parser.add_argument("path", help="packaged EPUB or expanded EPUB directory")
    parser.add_argument("--format", choices=("text", "json", "markdown"), default="text")
    parser.add_argument("--output", help="write stats output to a file")
    parser.add_argument("--estimate-pages", action="store_true", help="estimate pages from word count")
    parser.add_argument("--words-per-page", type=int, default=250, help="words-per-page divisor for page estimates")


def _add_help_and_version_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("-h", "-?", "--help", "-help", action="help", help="show this help message and exit")
    parser.add_argument("--version", "-version", action="store_true", help="show version and exit")


def _add_check_arguments(parser: argparse.ArgumentParser, *, legacy: bool) -> None:
    parser.add_argument(
        "path",
        nargs="?" if legacy else None,
        help="publication, package, or content document to validate",
    )
    parser.add_argument("--mode", "-m", choices=SUPPORTED_MODES, help="validation mode")
    parser.add_argument("-v", dest="epub_version", default="3.0", help="EPUB version")
    parser.add_argument(
        "--profile",
        "-p",
        choices=SUPPORTED_PROFILES,
        default="default",
        help="validation profile",
    )
    parser.add_argument("--save", action="store_true", help="save expanded EPUB as an archive")
    parser.add_argument("--out", "-o", "-out", dest="xml_report", help="XML report path or -")
    parser.add_argument("--json", "-j", dest="json_report", help="JSON report path or -")
    parser.add_argument("--xmp", "-x", dest="xmp_report", help="XMP report path or -")
    parser.add_argument("--quiet", "-q", action="store_true", help="suppress console output")
    parser.add_argument("--fatal", "-f", action="store_true", help="show only fatal messages")
    parser.add_argument("--error", "-e", action="store_true", help="show error and fatal messages")
    parser.add_argument("--warn", "-w", action="store_true", help="show warning, error, and fatal messages")
    parser.add_argument("--usage", "-u", action="store_true", help="include usage messages")
    parser.add_argument("--failonwarnings", action="store_true", help="exit 1 when warnings exist")
    parser.add_argument("--locale", help="report locale")
    parser.add_argument("--customMessages", "-c", dest="custom_messages", help="custom message file")
    summary_group = parser.add_mutually_exclusive_group()
    summary_group.add_argument(
        "--summary",
        dest="summary",
        action="store_true",
        default=True,
        help="show clean-run publication summary",
    )
    summary_group.add_argument(
        "--no-summary",
        dest="summary",
        action="store_false",
        help="disable clean-run publication summary",
    )


def _write_report(path: str | None, content: str) -> None:
    if not path:
        return
    if path == "-":
        sys.stdout.write(content)
        return
    Path(path).write_text(content, encoding="utf-8")


def _build_validation_config(args: argparse.Namespace, input_path: Path) -> ValidationConfig:
    return ValidationConfig(
        input_path=input_path,
        mode=args.mode or "auto",
        epub_version=args.epub_version,
        profile=args.profile,
        quiet=args.quiet,
        fail_on_warnings=args.failonwarnings,
        xml_report=args.xml_report,
        json_report=args.json_report,
        xmp_report=args.xmp_report,
        locale=args.locale,
        custom_messages=args.custom_messages,
    )


def _resolve_check_input(args: argparse.Namespace) -> tuple[Path | None, int | None]:
    if args.version:
        print(f"EPUBCheck v{__version__}")
        if not args.path:
            return None, 0
    if not args.path:
        build_legacy_parser().print_help()
        return None, 0

    report_targets = [value for value in (args.xml_report, args.json_report, args.xmp_report) if value]
    if len(report_targets) > 1:
        print("Only one output format can be specified at a time.", file=sys.stderr)
        return None, 1

    input_path = Path(args.path)
    if not input_path.exists():
        print(f"Input path not found: {args.path}", file=sys.stderr)
        return None, 1
    if args.save and args.mode and args.mode != "exp":
        print("--save requires --mode exp or no mode (auto-detect).", file=sys.stderr)
        return None, 1
    return input_path, None


def _maybe_save_input(args: argparse.Namespace, input_path: Path) -> None:
    if args.save and input_path.is_dir():
        DirectorySource.from_path(input_path).save()
    elif args.save and input_path.is_file():
        import tempfile
        import zipfile

        extract_dir = Path(tempfile.mkdtemp(prefix="pyepubcheck_"))
        with zipfile.ZipFile(input_path, "r") as zf:
            zf.extractall(extract_dir)
        DirectorySource.from_path(extract_dir).save()


def _apply_custom_overrides(report, custom_messages: str | None) -> None:
    overrides, override_errors = load_custom_message_overrides(custom_messages)
    messages = apply_custom_message_overrides(report.messages, overrides)
    if override_errors:
        messages.extend(override_errors)
    report.messages = messages


def _visible_messages(report, args: argparse.Namespace):
    visible_severities = {Severity.FATAL, Severity.ERROR, Severity.WARNING}
    if args.usage:
        visible_severities = {
            Severity.FATAL,
            Severity.ERROR,
            Severity.WARNING,
            Severity.INFO,
            Severity.USAGE,
        }
    elif args.warn:
        visible_severities = {Severity.FATAL, Severity.ERROR, Severity.WARNING}
    elif args.error:
        visible_severities = {Severity.FATAL, Severity.ERROR}
    elif args.fatal:
        visible_severities = {Severity.FATAL}
    return [message for message in report.messages if message.severity in visible_severities]


def _run_check(args: argparse.Namespace) -> int:
    input_path, early_exit = _resolve_check_input(args)
    if early_exit is not None:
        return early_exit
    assert input_path is not None

    _maybe_save_input(args, input_path)

    report = validate_path(args.path, config=_build_validation_config(args, input_path))
    _apply_custom_overrides(report, args.custom_messages)

    visible_messages = _visible_messages(report, args)
    if args.json_report:
        _write_report(args.json_report, render_json_report(report))
    if args.xml_report:
        _write_report(args.xml_report, render_xml_report(report))
    if args.xmp_report:
        _write_report(args.xmp_report, render_xmp_report(report))

    direct_report_to_stdout = any(target == "-" for target in (args.json_report, args.xml_report, args.xmp_report))
    if not args.quiet and not direct_report_to_stdout:
        stdout_text, stderr_text = render_console(report, locale=args.locale, messages=visible_messages)
        if args.summary and not visible_messages:
            try:
                summary = render_publication_summary(inspect_path(input_path))
            except Exception:
                summary = ""
            if summary:
                stdout_text = f"{stdout_text}\n\n{summary}"
        if stdout_text:
            print(stdout_text)
        if stderr_text:
            print(stderr_text, file=sys.stderr)

    visible_error = any(message.severity in {Severity.FATAL, Severity.ERROR} for message in visible_messages)
    visible_warning = any(message.severity is Severity.WARNING for message in visible_messages)
    if visible_error:
        return 1
    if args.failonwarnings and visible_warning:
        return 1
    return 0


def _parse_include(value: str) -> set[str]:
    parts = {item.strip() for item in value.split(",") if item.strip()}
    return parts or {"images", "metadata", "manifest", "nav", "stats", "container"}


def _filter_report_sections(report, sections: set[str]):
    return replace(
        report,
        metadata=report.metadata if "metadata" in sections else [],
        manifest=report.manifest if "manifest" in sections else [],
        images=report.images if "images" in sections else [],
        navigation=report.navigation if "nav" in sections else None,
        stats=report.stats if "stats" in sections else None,
        container=(
            report.container
            if "container" in sections
            else replace(report.container, rootfiles=[], total_entries=0, total_bytes=0)
        ),
    )


def _limit_report(report, limit: int | None):
    if limit is None or limit <= 0:
        return report
    navigation = report.navigation
    if navigation is not None:
        navigation = replace(
            navigation,
            toc_entries=navigation.toc_entries[:limit],
            page_list_entries=navigation.page_list_entries[:limit],
            landmark_entries=navigation.landmark_entries[:limit],
        )
    stats = report.stats
    if stats is not None:
        stats = replace(stats, per_document=stats.per_document[:limit])
    return replace(
        report,
        manifest=report.manifest[:limit],
        images=report.images[:limit],
        metadata=report.metadata[:limit],
        navigation=navigation,
        stats=stats,
    )


def _sort_images(images: list, key_name: str) -> list:
    key_funcs = {
        "path": lambda image: image.path,
        "size": lambda image: image.size_bytes or -1,
        "width": lambda image: image.width or -1,
        "height": lambda image: image.height or -1,
        "pixels": lambda image: (image.width or 0) * (image.height or 0),
        "format": lambda image: image.format,
    }
    reverse = key_name in {"size", "width", "height", "pixels"}
    return sorted(images, key=key_funcs[key_name], reverse=reverse)


def _sort_manifest(manifest: list, key_name: str) -> list:
    key_funcs = {
        "path": lambda asset: asset.path,
        "size": lambda asset: asset.size_bytes or -1,
        "type": lambda asset: asset.media_type,
    }
    reverse = key_name == "size"
    return sorted(manifest, key=key_funcs[key_name], reverse=reverse)


def _render_json_payload(payload: dict[str, object]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _validation_summary(path: str | Path) -> dict[str, object]:
    report = validate_path(path)
    return {
        "exitCode": report.exit_code(),
        "messageCount": len(report.messages),
        "errorCount": sum(1 for message in report.messages if message.severity in {Severity.FATAL, Severity.ERROR}),
        "warningCount": sum(1 for message in report.messages if message.severity is Severity.WARNING),
    }


def _run_inspect(args: argparse.Namespace) -> int:
    report = inspect_path(args.path, estimate_pages=args.estimate_pages, words_per_page=args.words_per_page)
    report = _filter_report_sections(report, _parse_include(args.include))
    if args.sort == "path":
        report = replace(
            report,
            images=_sort_images(report.images, "path"),
            manifest=_sort_manifest(report.manifest, "path"),
        )
    elif args.sort == "size":
        report = replace(
            report,
            images=_sort_images(report.images, "size"),
            manifest=_sort_manifest(report.manifest, "size"),
        )
    elif args.sort == "type":
        report = replace(
            report,
            images=_sort_images(report.images, "format"),
            manifest=_sort_manifest(report.manifest, "type"),
        )
    report = _limit_report(report, args.limit)

    validation = _validation_summary(args.path) if args.validate else None
    if args.format == "json":
        payload = inspection_report_to_data(report)
        if validation is not None:
            payload["validation"] = validation
        content = _render_json_payload(payload)
    elif args.format == "markdown":
        content = render_inspection_markdown(report)
        if validation is not None:
            content += (
                "\n## Validation\n\n"
                f"- Exit code: {validation['exitCode']}\n"
                f"- Messages: {validation['messageCount']}\n"
                f"- Errors: {validation['errorCount']}\n"
                f"- Warnings: {validation['warningCount']}\n"
            )
    else:
        content = render_inspection_text(report)
        if validation is not None:
            content += (
                "\nValidation\n"
                f"  Exit code: {validation['exitCode']}\n"
                f"  Messages: {validation['messageCount']}\n"
                f"  Errors: {validation['errorCount']}\n"
                f"  Warnings: {validation['warningCount']}\n"
            )
    _write_report(args.output or "-", content)
    return int(validation["exitCode"]) if validation is not None else 0


def _run_images(args: argparse.Namespace) -> int:
    report = inspect_path(args.path)
    images = list(report.images)
    if args.min_width is not None:
        images = [image for image in images if image.width is not None and image.width >= args.min_width]
    if args.min_height is not None:
        images = [image for image in images if image.height is not None and image.height >= args.min_height]
    if args.max_width is not None:
        images = [image for image in images if image.width is not None and image.width <= args.max_width]
    if args.max_height is not None:
        images = [image for image in images if image.height is not None and image.height <= args.max_height]
    if args.max_bytes is not None:
        images = [image for image in images if image.size_bytes is not None and image.size_bytes <= args.max_bytes]
    if args.image_format:
        requested = args.image_format.upper()
        images = [image for image in images if image.format == requested]
    if args.referenced_only:
        images = [image for image in images if image.referenced_by]
    if args.unreferenced_only:
        images = [image for image in images if not image.referenced_by]
    if args.cover_only:
        images = [image for image in images if "cover-image" in image.properties]
    images = _sort_images(images, "size" if args.largest else args.sort)
    if args.largest:
        images = images[: args.largest]

    selected = replace(report, metadata=[], manifest=[], images=images, navigation=None, stats=None)
    if args.format == "json":
        content = _render_json_payload(
            {
                "inputPath": report.input_path,
                "images": inspection_report_to_data(selected)["images"],
            }
        )
    elif args.format == "csv":
        content = render_images_csv(images)
    elif args.format == "markdown":
        content = render_inspection_markdown(selected)
    else:
        content = render_images_text(report.input_path, images)
    _write_report(args.output or "-", content)
    return 0


def _run_metadata(args: argparse.Namespace) -> int:
    report = inspect_path(args.path)
    _ = inspect_metadata(args.path)
    selected = replace(report, manifest=[], images=[], navigation=None, stats=None)
    if args.format == "json":
        payload = inspection_report_to_data(selected)
        payload["manifest"] = []
        payload["images"] = []
        content = _render_json_payload(payload)
    elif args.format == "markdown":
        content = render_inspection_markdown(selected)
    else:
        content = render_metadata_text(report.input_path, report.metadata, report.packages)
    _write_report(args.output or "-", content)
    return 0


def _run_manifest(args: argparse.Namespace) -> int:
    report = inspect_path(args.path)
    manifest = _sort_manifest(report.manifest, args.sort)
    selected = replace(report, metadata=[], manifest=manifest, images=[], navigation=None, stats=None)
    if args.format == "json":
        payload = inspection_report_to_data(selected)
        payload["metadata"] = []
        payload["images"] = []
        content = _render_json_payload(payload)
    elif args.format == "csv":
        content = render_manifest_csv(manifest)
    elif args.format == "markdown":
        content = render_inspection_markdown(selected)
    else:
        content = render_manifest_text(report.input_path, manifest)
    _write_report(args.output or "-", content)
    return 0


def _run_nav(args: argparse.Namespace) -> int:
    report = inspect_path(args.path)
    selected = replace(report, metadata=[], manifest=[], images=[], stats=None)
    if args.format == "json":
        payload = inspection_report_to_data(selected)
        payload["metadata"] = []
        payload["manifest"] = []
        payload["images"] = []
        content = _render_json_payload(payload)
    elif args.format == "markdown":
        content = render_inspection_markdown(selected)
    else:
        content = (
            render_navigation_text(report.input_path, report.navigation)
            if report.navigation
            else "Navigation unavailable\n"
        )
    _write_report(args.output or "-", content)
    return 0


def _run_stats(args: argparse.Namespace) -> int:
    report = inspect_path(args.path, estimate_pages=args.estimate_pages, words_per_page=args.words_per_page)
    selected = replace(report, metadata=[], manifest=[], images=[], navigation=None)
    if args.format == "json":
        payload = inspection_report_to_data(selected)
        payload["metadata"] = []
        payload["manifest"] = []
        payload["images"] = []
        content = _render_json_payload(payload)
    elif args.format == "markdown":
        content = render_inspection_markdown(selected)
    else:
        content = render_stats_text(report.input_path, report.stats)
    _write_report(args.output or "-", content)
    return 0


def main(argv: list[str] | None = None) -> int:
    raw_args = list(argv) if argv is not None else sys.argv[1:]
    if not raw_args:
        build_parser().print_help()
        return 0
    if raw_args[0] in KNOWN_COMMANDS:
        parser = build_parser()
        args = parser.parse_args(raw_args)
        if args.command == "check":
            return _run_check(args)
        if args.command == "inspect":
            return _run_inspect(args)
        if args.command == "images":
            return _run_images(args)
        if args.command == "metadata":
            return _run_metadata(args)
        if args.command == "manifest":
            return _run_manifest(args)
        if args.command == "nav":
            return _run_nav(args)
        if args.command == "stats":
            return _run_stats(args)
        if args.version:
            print(f"EPUBCheck v{__version__}")
            return 0
        parser.print_help()
        return 0

    args = build_legacy_parser().parse_args(raw_args)
    return _run_check(args)
