"""EDUPUB profile checks."""

from __future__ import annotations

from pathlib import Path

from pyepubcheck.messages import build_message
from pyepubcheck.result import ResultMessage
from pyepubcheck.xml_parser import load_xml


def _validate_edupub_page_list(path: Path, root) -> list[ResultMessage]:
    """Validate EDUPUB page list requirement."""
    errors: list[ResultMessage] = []

    # Find nav elements
    for nav in root.iter("{http://www.w3.org/1999/xhtml}nav"):
        epub_type = nav.get("{http://www.idpf.org/2007/ops}type", "")
        if not epub_type:
            epub_type = nav.get("epub:type", "")

        if "page-list" in epub_type:
            return []

    # No page-list nav found
    errors.append(
        build_message(
            "NAV-003",
            path=str(path),
            message="EDUPUB page list missing",
        )
    )

    return errors


def _validate_edupub_toc(path: Path, root) -> list[ResultMessage]:
    """Validate EDUPUB TOC requirement."""
    errors: list[ResultMessage] = []

    # Find nav elements
    for nav in root.iter("{http://www.w3.org/1999/xhtml}nav"):
        epub_type = nav.get("{http://www.idpf.org/2007/ops}type", "")
        if not epub_type:
            epub_type = nav.get("epub:type", "")

        if "toc" in epub_type:
            return []

    # No toc nav found
    errors.append(
        build_message(
            "RSC-005",
            path=str(path),
            message="EDUPUB TOC missing",
        )
    )

    return errors


def run(path: str | Path, *, profile: str = "default") -> list[ResultMessage]:
    """Run EDUPUB profile checks."""
    candidate = Path(path)
    errors: list[ResultMessage] = []

    # Only run for EDUPUB profile
    if profile != "edupub":
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

    # Check if this is a navigation document
    is_nav = False
    for nav in root.iter("{http://www.w3.org/1999/xhtml}nav"):
        is_nav = True
        break

    if not is_nav:
        return []

    # Validate page list
    errors.extend(_validate_edupub_page_list(candidate, root))

    # Validate TOC
    errors.extend(_validate_edupub_toc(candidate, root))

    return errors
