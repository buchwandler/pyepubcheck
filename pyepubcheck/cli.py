"""Command-line entrypoint."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from pyepubcheck import __version__
from pyepubcheck.api import validate_path
from pyepubcheck.config import ValidationConfig
from pyepubcheck.io.expanded import DirectorySource
from pyepubcheck.messages import (
    apply_custom_message_overrides,
    load_custom_message_overrides,
)
from pyepubcheck.registry import SUPPORTED_MODES, SUPPORTED_PROFILES
from pyepubcheck.reports.console import render_console
from pyepubcheck.reports.json_report import render_json_report
from pyepubcheck.reports.xml_report import render_xml_report
from pyepubcheck.reports.xmp_report import render_xmp_report
from pyepubcheck.severity import Severity


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pyepubcheck", add_help=False)
    parser.add_argument("-h", "-?", "--help", "-help", action="help", help="show this help message and exit")
    parser.add_argument("--version", "-version", action="store_true", help="show version and exit")
    parser.add_argument("path", nargs="?", help="publication, package, or content document to validate")
    parser.add_argument("--mode", "-m", choices=SUPPORTED_MODES[1:], help="validation mode")
    parser.add_argument("-v", dest="epub_version", default="3.0", help="EPUB version")
    parser.add_argument("--profile", "-p", choices=SUPPORTED_PROFILES, default="default", help="validation profile")
    parser.add_argument("--save", action="store_true", help="save expanded EPUB as an archive")
    parser.add_argument("--out", "-o", dest="xml_report", help="XML report path or -")
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
    return parser


def _write_report(path: str | None, content: str) -> None:
    if not path:
        return
    if path == "-":
        sys.stdout.write(content)
        return
    Path(path).write_text(content, encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.version:
        print(f"EPUBCheck v{__version__}")
        if not args.path:
            return 0
    if not args.path:
        parser.print_help()
        return 0
    report_targets = [value for value in (args.xml_report, args.json_report, args.xmp_report) if value]
    if len(report_targets) > 1:
        print("Only one output format can be specified at a time.", file=sys.stderr)
        return 1
    input_path = Path(args.path)
    if not input_path.exists():
        print(f"Input path not found: {args.path}", file=sys.stderr)
        return 1
    if args.save and (args.mode != "exp" or not input_path.is_dir()):
        print("--save requires --mode exp and an expanded EPUB directory.", file=sys.stderr)
        return 1
    if args.save:
        DirectorySource.from_path(input_path).save()

    config = ValidationConfig(
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
    report = validate_path(args.path, config=config)
    overrides, override_errors = load_custom_message_overrides(args.custom_messages)
    messages = apply_custom_message_overrides(report.messages, overrides)
    if override_errors:
        messages.extend(override_errors)
    report.messages = messages

    visible_severities = {Severity.FATAL, Severity.ERROR, Severity.WARNING}
    if args.usage:
        visible_severities = {Severity.FATAL, Severity.ERROR, Severity.WARNING, Severity.INFO, Severity.USAGE}
    elif args.warn:
        visible_severities = {Severity.FATAL, Severity.ERROR, Severity.WARNING}
    elif args.error:
        visible_severities = {Severity.FATAL, Severity.ERROR}
    elif args.fatal:
        visible_severities = {Severity.FATAL}
    visible_messages = [message for message in report.messages if message.severity in visible_severities]

    _write_report(args.json_report, render_json_report(report))
    _write_report(args.xml_report, render_xml_report(report))
    _write_report(args.xmp_report, render_xmp_report(report))

    direct_report_to_stdout = any(target == "-" for target in (args.json_report, args.xml_report, args.xmp_report))
    if not args.quiet and not direct_report_to_stdout:
        stdout_text, stderr_text = render_console(report, locale=args.locale, messages=visible_messages)
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
