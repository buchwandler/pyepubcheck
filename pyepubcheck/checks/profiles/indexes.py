"""Index profile checks."""

from __future__ import annotations

from pathlib import Path

from pyepubcheck.messages import build_message
from pyepubcheck.result import ResultMessage
from pyepubcheck.xml_parser import load_xml


def _validate_index_element(path: Path, root) -> list[ResultMessage]:
    """Validate index element presence."""
    errors: list[ResultMessage] = []

    # Find index elements
    has_index = False
    for el in root.iter("{http://www.w3.org/1999/xhtml}div"):
        epub_type = el.get("{http://www.idpf.org/2007/ops}type", "")
        if not epub_type:
            epub_type = el.get("epub:type", "")
        if "index" in epub_type:
            has_index = True
            break

    if not has_index:
        errors.append(
            build_message(
                "RSC-005",
                path=str(path),
                message='At least one "index" element must be present in a document declared as an index in the OPF',
            )
        )

    return errors


def run(path: str | Path, *, profile: str = "default") -> list[ResultMessage]:
    """Run index profile checks."""
    candidate = Path(path)
    errors: list[ResultMessage] = []

    # Only run for index profile
    if profile != "idx":
        return []

    # Only check XHTML files
    if candidate.suffix.lower() not in (".xhtml", ".html"):
        return []

    # Load and parse XML
    xml_doc = load_xml(candidate)
    if xml_doc.errors:
        return xml_doc.errors

    root = xml_doc.root

    # Check if this is an XHTML document
    if xml_doc.doc_type != "xhtml":
        return []

    # Validate index element
    errors.extend(_validate_index_element(candidate, root))

    return errors
