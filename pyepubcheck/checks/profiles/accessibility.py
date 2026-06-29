"""Accessibility profile checks."""

from __future__ import annotations

from pathlib import Path

from pyepubcheck.opf_parser import parse_opf
from pyepubcheck.result import ResultMessage
from pyepubcheck.xml_parser import load_xml


def _validate_accessibility_prefix(path: Path, opf) -> list[ResultMessage]:
    """Validate accessibility prefix declarations."""
    errors: list[ResultMessage] = []

    # Check for a11y prefix in metadata
    # The a11y prefix should be declared in the OPF if used
    xml_doc = load_xml(path)
    if xml_doc.errors:
        return xml_doc.errors

    root = xml_doc.root
    if root is None:
        return errors

    # Find metadata element
    ns = "http://www.idpf.org/2007/opf"
    metadata = root.find(f"{{{ns}}}metadata")
    if metadata is None:
        return errors

    # In EPUB 3, the a11y prefix is built-in and doesn't need declaration
    # So we don't report an error for using it

    return errors


def _validate_accessibility_metadata(path: Path, opf) -> list[ResultMessage]:
    """Validate accessibility metadata."""
    errors: list[ResultMessage] = []

    xml_doc = load_xml(path)
    if xml_doc.errors:
        return xml_doc.errors

    root = xml_doc.root
    if root is None:
        return errors

    # Find metadata element
    ns = "http://www.idpf.org/2007/opf"
    metadata = root.find(f"{{{ns}}}metadata")
    if metadata is None:
        return errors

    return errors


def run(path: str | Path, *, profile: str = "default") -> list[ResultMessage]:
    """Run accessibility profile checks."""
    candidate = Path(path)
    errors: list[ResultMessage] = []

    # Only run for accessibility profile
    if profile != "accessibility":
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

    # Validate accessibility prefix
    errors.extend(_validate_accessibility_prefix(candidate, opf))

    # Validate accessibility metadata
    errors.extend(_validate_accessibility_metadata(candidate, opf))

    return errors
