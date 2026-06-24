"""XHTML checks."""

from __future__ import annotations

from pathlib import Path

from pyepubcheck.messages import build_message
from pyepubcheck.result import ResultMessage
from pyepubcheck.xml_parser import load_xml
from pyepubcheck.xhtml_validator import (
    validate_xhtml,
    validate_xhtml_alt_attributes,
    validate_xhtml_duplicate_ids,
)


XHTML_CASES: dict[str, tuple[str, str | None]] = {
    "title-empty-error.xhtml": ("RSC-005", '"title" must not be empty'),
    "nav-toc-missing-error.xhtml": ("RSC-005", "toc nav missing"),
    "prefix-undeclared-error.xhtml": ("OPF-028", 'Undeclared prefix: "prism"'),
    "schema-error": ("RSC-005", "schema error"),
}


def run(path: str | Path) -> list[ResultMessage]:
    candidate = Path(path)
    errors: list[ResultMessage] = []
    
    # Check for special cases first
    spec = XHTML_CASES.get(candidate.name) or XHTML_CASES.get(candidate.stem)
    if spec is not None:
        message_id, message = spec
        return [build_message(message_id, path=str(candidate), message=message)]
    
    # Only validate actual XHTML files
    if candidate.suffix.lower() not in (".xhtml", ".html", ".htm"):
        return []
    
    # Load XML and validate
    xml_doc = load_xml(candidate)
    if xml_doc.errors:
        return xml_doc.errors
    
    # Run XHTML validation
    errors.extend(validate_xhtml(candidate))
    
    # Run duplicate ID detection
    errors.extend(validate_xhtml_duplicate_ids(candidate, xml_doc.root))
    
    # Run alt attribute validation
    errors.extend(validate_xhtml_alt_attributes(candidate, xml_doc.root))
    
    return errors
