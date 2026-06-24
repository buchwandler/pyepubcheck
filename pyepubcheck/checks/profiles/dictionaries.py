"""Dictionary profile checks."""

from __future__ import annotations

from pathlib import Path

from pyepubcheck.messages import build_message
from pyepubcheck.opf_parser import parse_opf
from pyepubcheck.result import ResultMessage
from pyepubcheck.xml_parser import load_xml


def _validate_dictionary_dc_type(path: Path, opf) -> list[ResultMessage]:
    """Validate dictionary dc:type requirement."""
    errors: list[ResultMessage] = []

    # Check for dictionary dc:type
    has_dict_type = any("dictionary" in t for t in opf.metadata.types)

    if not has_dict_type:
        errors.append(
            build_message(
                "RSC-005",
                path=str(path),
                message='The dc:type identifier "dictionary" is required.',
            )
        )
        errors.append(
            build_message(
                "OPF-079",
                path=str(path),
                message="dictionary metadata warning",
            )
        )

    return errors


def run(path: str | Path, *, profile: str = "default") -> list[ResultMessage]:
    """Run dictionary profile checks."""
    candidate = Path(path)
    errors: list[ResultMessage] = []

    # Only run for dictionary profile
    if profile != "dict":
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

    # Validate dictionary dc:type
    errors.extend(_validate_dictionary_dc_type(candidate, opf))

    return errors
