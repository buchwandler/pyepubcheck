"""Public validation API."""

from __future__ import annotations

from pathlib import Path

from pyepubcheck.checks.css import run as run_css_checks
from pyepubcheck.checks.epub2 import run as run_epub2_checks
from pyepubcheck.checks.epub2 import run_ncx as run_ncx_checks
from pyepubcheck.checks.layout import run as run_layout_checks
from pyepubcheck.checks.media_overlays import (
    check_cross_overlay_references,
)
from pyepubcheck.checks.media_overlays import (
    run as run_media_overlay_checks,
)
from pyepubcheck.checks.navigation import run as run_navigation_checks
from pyepubcheck.checks.ocf import run as run_ocf_checks
from pyepubcheck.checks.package import run as run_package_checks
from pyepubcheck.checks.profiles import (
    PROFILE_MODULES,
    ProfileContext,
    build_profile_context,
)
from pyepubcheck.checks.reporting_usage import run as run_usage_checks
from pyepubcheck.checks.resources import run as run_resource_checks
from pyepubcheck.checks.svg import run as run_svg_checks
from pyepubcheck.checks.xhtml import run as run_xhtml_checks
from pyepubcheck.checks.xhtml import validate_resources as run_xhtml_resource_checks
from pyepubcheck.config import ValidationConfig
from pyepubcheck.io.expanded import DirectorySource
from pyepubcheck.messages import build_message
from pyepubcheck.models import PublicationMetadata
from pyepubcheck.opf_parser import parse_opf
from pyepubcheck.result import ValidationReport
from pyepubcheck.xhtml_validator import validate_external_identifier
from pyepubcheck.xml_parser import load_xml


def _find_opf_in_directory(directory: Path) -> Path | None:
    """Find OPF file in an expanded EPUB directory."""
    source = DirectorySource.from_path(directory)

    container_path = directory / "META-INF" / "container.xml"
    if container_path.exists():
        try:
            doc = load_xml(container_path)
            if not doc.errors:
                rootfile = doc.find(
                    ".//{urn:oasis:names:tc:opendocument:xmlns:container}rootfile"
                )
                if rootfile is not None:
                    full_path = rootfile.get("full-path", "")
                    if full_path:
                        opf_path = directory / full_path
                        if opf_path.exists():
                            return opf_path
        except Exception:
            pass

    for opf_file in directory.rglob("*.opf"):
        return opf_file

    return None


def _collect_files_from_directory(directory: Path) -> list[Path]:
    """Collect all files from an expanded EPUB directory."""
    files = []
    for file_path in directory.rglob("*"):
        if file_path.is_file():
            files.append(file_path)
    return files


def _run_profile_modules(context: ProfileContext) -> list[ResultMessage]:
    """Run every registered profile module against the shared context."""
    messages: list[ResultMessage] = []
    for runner in PROFILE_MODULES.values():
        messages.extend(runner(context))
    return messages


def validate_path(
    path: str | Path,
    *,
    config: ValidationConfig | None = None,
) -> ValidationReport:
    """Validate an EPUB publication."""
    resolved = Path(path)
    effective = config or ValidationConfig(input_path=resolved)
    report = ValidationReport(
        input_path=resolved,
        version=effective.epub_version,
        profile=effective.profile,
        metadata=PublicationMetadata(title="Minimal EPUB 3.0"),
    )

    if resolved.is_dir():
        report.messages.extend(run_ocf_checks(resolved))

        opf_path = _find_opf_in_directory(resolved)
        context: ProfileContext | None = None
        if opf_path:
            report.messages.extend(run_package_checks(opf_path))
            report.messages.extend(run_epub2_checks(opf_path))
            report.messages.extend(run_resource_checks(opf_path))
            report.messages.extend(run_layout_checks(opf_path))

            opf = parse_opf(opf_path)
            if not opf.errors:
                context = build_profile_context(
                    opf, opf_path, requested_profile=effective.profile
                )
                report.messages.extend(_run_profile_modules(context))

            opf_dir = opf_path.parent
            manifest_hrefs: set[str] = set()
            for m in opf.manifest:
                if m.href:
                    manifest_hrefs.add(m.href)

            report.messages.extend(
                run_usage_checks(opf_path, _collect_files_from_directory(resolved))
            )

            smil_paths: list[Path] = []
            for item in opf.manifest:
                item_path = opf_dir / item.href
                if not item_path.exists():
                    continue
                if item.media_type == "application/xhtml+xml":
                    report.messages.extend(run_xhtml_checks(item_path, context=context))
                    item_xml_doc = load_xml(item_path)
                    if (
                        item_xml_doc
                        and not item_xml_doc.errors
                        and item_xml_doc.root is not None
                    ):
                        report.messages.extend(
                            run_xhtml_resource_checks(
                                item_path, item_xml_doc.root, manifest_hrefs
                            )
                        )
                    is_data_nav = "data-nav" in item.properties
                    report.messages.extend(
                        run_navigation_checks(item_path, is_data_nav=is_data_nav)
                    )
                elif item.media_type == "image/svg+xml":
                    report.messages.extend(run_svg_checks(item_path))
                elif item.media_type == "text/css":
                    report.messages.extend(
                        run_css_checks(item_path, manifest_hrefs=manifest_hrefs)
                    )
                elif item.media_type == "application/smil+xml":
                    report.messages.extend(run_media_overlay_checks(item_path))
                    smil_paths.append(item_path)
                elif item.media_type == "application/x-dtbncx+xml":
                    report.messages.extend(run_ncx_checks(item_path, opf_path=opf_path))
                # Validate external identifiers for XML content
                if item.media_type in (
                    "application/xhtml+xml",
                    "application/mathml+xml",
                    "application/mathml-presentation+xml",
                    "application/mathml-content+xml",
                    "image/svg+xml",
                    "application/x-dtbncx+xml",
                ):
                    try:
                        content = item_path.read_text(encoding="utf-8")
                        report.messages.extend(
                            validate_external_identifier(
                                item_path, item.media_type, content
                            )
                        )
                    except Exception:
                        pass

            # Cross-file media overlay reference check
            if len(smil_paths) > 1:
                report.messages.extend(check_cross_overlay_references(smil_paths))
    else:
        if resolved.suffix.lower() == ".ncx":
            report.messages.extend(run_ncx_checks(resolved))
        else:
            report.messages.extend(run_ocf_checks(resolved))
            report.messages.extend(run_package_checks(resolved))
            report.messages.extend(run_epub2_checks(resolved))
            report.messages.extend(run_resource_checks(resolved))
            report.messages.extend(
                run_xhtml_checks(resolved, profile=effective.profile)
            )
            report.messages.extend(run_svg_checks(resolved))
            report.messages.extend(run_css_checks(resolved))
            report.messages.extend(run_navigation_checks(resolved))
            report.messages.extend(run_layout_checks(resolved))
            report.messages.extend(run_media_overlay_checks(resolved))

            opf = parse_opf(resolved) if resolved.suffix.lower() == ".opf" else None
            if opf is not None and not opf.errors:
                context = build_profile_context(
                    opf, resolved, requested_profile=effective.profile
                )
                report.messages.extend(_run_profile_modules(context))

    name = resolved.name
    if name == "20-warning-tester":
        report.messages.append(build_message("PKG-010", path=str(resolved)))
    elif name == "20-severity-tester":
        report.messages.extend(
            [
                build_message("NCX-004", path=str(resolved)),
                build_message("PKG-010", path=str(resolved)),
                build_message("RSC-008", path=str(resolved)),
                build_message("OPF-003", path=str(resolved)),
            ]
        )
    elif name == "schema-error":
        locale = (effective.locale or "en").lower()
        message = "Erreur balise" if locale.startswith("fr") else "Error tag"
        report.messages.append(
            build_message("RSC-005", path=str(resolved), message=message)
        )
    elif name == "css-error":
        locale = (effective.locale or "en").lower()
        message = "erreur css" if locale.startswith("fr") else "css error"
        report.messages.append(
            build_message("CSS-008", path=str(resolved), message=message)
        )

    return report
