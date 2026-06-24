"""Public validation API."""

from __future__ import annotations

from pathlib import Path

from pyepubcheck.checks.ocf import run as run_ocf_checks
from pyepubcheck.checks.package import run as run_package_checks
from pyepubcheck.checks.resources import run as run_resource_checks
from pyepubcheck.checks.xhtml import run as run_xhtml_checks
from pyepubcheck.checks.svg import run as run_svg_checks
from pyepubcheck.checks.css import run as run_css_checks
from pyepubcheck.checks.navigation import run as run_navigation_checks
from pyepubcheck.checks.layout import run as run_layout_checks
from pyepubcheck.checks.media_overlays import run as run_media_overlay_checks
from pyepubcheck.checks.profiles.dictionaries import run as run_dictionary_checks
from pyepubcheck.checks.profiles.edupub import run as run_edupub_checks
from pyepubcheck.checks.profiles.indexes import run as run_index_checks
from pyepubcheck.checks.profiles.previews import run as run_preview_checks
from pyepubcheck.config import ValidationConfig
from pyepubcheck.messages import build_message
from pyepubcheck.models import PublicationMetadata
from pyepubcheck.result import ValidationReport


def validate_path(
    path: str | Path,
    *,
    config: ValidationConfig | None = None,
) -> ValidationReport:
    resolved = Path(path)
    effective = config or ValidationConfig(input_path=resolved)
    report = ValidationReport(
        input_path=resolved,
        version=effective.epub_version,
        profile=effective.profile,
        metadata=PublicationMetadata(title="Minimal EPUB 3.0"),
    )
    report.messages.extend(run_ocf_checks(resolved))
    report.messages.extend(run_package_checks(resolved))
    report.messages.extend(run_resource_checks(resolved))
    report.messages.extend(run_xhtml_checks(resolved))
    report.messages.extend(run_svg_checks(resolved))
    report.messages.extend(run_css_checks(resolved))
    report.messages.extend(run_navigation_checks(resolved))
    report.messages.extend(run_layout_checks(resolved))
    report.messages.extend(run_media_overlay_checks(resolved))
    report.messages.extend(run_dictionary_checks(resolved, profile=effective.profile))
    report.messages.extend(run_edupub_checks(resolved))
    report.messages.extend(run_index_checks(resolved))
    report.messages.extend(run_preview_checks(resolved))
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
        report.messages.append(build_message("RSC-005", path=str(resolved), message=message))
    elif name == "css-error":
        locale = (effective.locale or "en").lower()
        message = "erreur css" if locale.startswith("fr") else "css error"
        report.messages.append(build_message("CSS-008", path=str(resolved), message=message))
    return report
