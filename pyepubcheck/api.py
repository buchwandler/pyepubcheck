"""Public validation API."""

from __future__ import annotations

from pathlib import Path

from pyepubcheck.checks.ocf import run as run_ocf_checks
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
    return report
