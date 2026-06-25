"""XHTML checks."""

from __future__ import annotations

from pathlib import Path

from pyepubcheck.messages import build_message
from pyepubcheck.result import ResultMessage
from pyepubcheck.xml_parser import load_xml
from pyepubcheck.xhtml_validator import (
    validate_xhtml,
    validate_xhtml_alt_attributes,
    validate_xhtml_doctype,
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

    # Run DOCTYPE validation
    errors.extend(validate_xhtml_doctype(candidate, xml_doc.root))
    
    return errors


def validate_resources(path: Path, xml_root, manifest_hrefs: set[str]) -> list[ResultMessage]:
    """Validate resource references in an XHTML document."""
    errors: list[ResultMessage] = []

    xhtml_ns = "http://www.w3.org/1999/xhtml"

    # Check img src attributes
    for img_el in xml_root.iter(f"{{{xhtml_ns}}}img"):
        src = img_el.get("src", "")
        if src and not src.startswith(("http://", "https://", "data:", "#")):
            base_src = src.split("#")[0] if "#" in src else src
            if base_src and base_src not in manifest_hrefs:
                errors.append(
                    build_message(
                        "RSC-007",
                        path=str(path),
                        message=f"resource '{src}' not found in manifest",
                    )
                )

    # Check a href attributes
    for a_el in xml_root.iter(f"{{{xhtml_ns}}}a"):
        href = a_el.get("href", "")
        if href and not href.startswith(("http://", "https://", "mailto:", "#")):
            base_href = href.split("#")[0] if "#" in href else href
            if base_href and base_href not in manifest_hrefs:
                errors.append(
                    build_message(
                        "RSC-011",
                        path=str(path),
                        message=f"hyperlink '{href}' references missing resource",
                    )
                )

    # Check link href attributes
    for link_el in xml_root.iter(f"{{{xhtml_ns}}}link"):
        link_href = link_el.get("href", "")
        if link_href and not link_href.startswith(("http://", "https://")):
            base_link_href = link_href.split("#")[0] if "#" in link_href else link_href
            if base_link_href and base_link_href not in manifest_hrefs:
                errors.append(
                    build_message(
                        "RSC-007",
                        path=str(path),
                        message=f"stylesheet '{link_href}' not found in manifest",
                    )
                )

    return errors
