"""Preview profile checks."""

from __future__ import annotations

from pathlib import Path

from pyepubcheck.messages import build_message
from pyepubcheck.opf_parser import parse_opf
from pyepubcheck.result import ResultMessage
from pyepubcheck.xml_parser import load_xml


def _validate_preview_dc_type(path: Path, opf) -> list[ResultMessage]:
    """Validate preview dc:type requirement."""
    errors: list[ResultMessage] = []

    # Check for preview dc:type
    has_preview_type = any("preview" in t for t in opf.metadata.types)

    if not has_preview_type:
        errors.append(
            build_message(
                "RSC-005",
                path=str(path),
                message='An EPUB Preview publication must have a "preview" dc:type',
            )
        )

    return errors


def run(path: str | Path, *, profile: str = "default") -> list[ResultMessage]:
    """Run preview profile checks."""
    candidate = Path(path)
    errors: list[ResultMessage] = []

    # Only run for preview profile
    if profile != "preview":
        return []

    # Only check OPF files
    if candidate.suffix.lower() != ".opf":
        return []

    # Load and parse XML
    xml_doc = load_xml(candidate)
    if xml_doc.errors:
        return xml_doc.errors

    # Check if this is an OPF document
    if xml_doc.doc_type != "opf":
        return []

    # Parse OPF
    opf = parse_opf(candidate)
    if opf.errors:
        return opf.errors

    # Validate preview dc:type
    errors.extend(_validate_preview_dc_type(candidate, opf))

    return errors
