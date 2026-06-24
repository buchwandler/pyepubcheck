"""Navigation-document checks."""

from __future__ import annotations

from pathlib import Path

from pyepubcheck.messages import build_message
from pyepubcheck.result import ResultMessage
from pyepubcheck.xml_parser import XHTML_NS, load_xml


def _validate_nav_toc(path: Path, root) -> list[ResultMessage]:
    """Validate navigation document TOC."""
    errors: list[ResultMessage] = []

    # Find nav elements
    nav_elements = list(root.iter("{http://www.w3.org/1999/xhtml}nav"))
    if not nav_elements:
        nav_elements = list(root.iter("nav"))

    if not nav_elements:
        errors.append(
            build_message(
                "RSC-005",
                path=str(path),
                message="toc nav missing",
            )
        )
        return errors

    # Check for toc nav
    has_toc = False
    for nav in nav_elements:
        epub_type = nav.get("{http://www.idpf.org/2007/ops}type", "")
        if not epub_type:
            epub_type = nav.get("epub:type", "")
        if "toc" in epub_type:
            has_toc = True
            break

    if not has_toc:
        errors.append(
            build_message(
                "RSC-005",
                path=str(path),
                message="toc nav missing",
            )
        )

    return errors


def _validate_nav_type(path: Path, root) -> list[ResultMessage]:
    """Validate navigation document type attributes."""
    errors: list[ResultMessage] = []

    # Find nav elements
    for nav in root.iter("{http://www.w3.org/1999/xhtml}nav"):
        epub_type = nav.get("{http://www.idpf.org/2007/ops}type", "")
        if not epub_type:
            epub_type = nav.get("epub:type", "")

        # Check for data nav without type
        if not epub_type:
            errors.append(
                build_message(
                    "RSC-005",
                    path=str(path),
                    message='A "nav" element in a Data Navigation Document must have an "epub:type" attribute',
                )
            )

    return errors


def _validate_nav_structure(path: Path, root) -> list[ResultMessage]:
    """Validate navigation document structure."""
    errors: list[ResultMessage] = []

    # Find nav elements
    for nav in root.iter("{http://www.w3.org/1999/xhtml}nav"):
        epub_type = nav.get("{http://www.idpf.org/2007/ops}type", "")
        if not epub_type:
            epub_type = nav.get("epub:type", "")

        # Check for region-based nav structure
        if "region-based" in epub_type:
            ol_children = [el for el in nav if el.tag.endswith("}ol") or el.tag == "ol"]
            if len(ol_children) != 1:
                errors.append(
                    build_message(
                        "RSC-005",
                        path=str(path),
                        message="A region-based nav element must contain exactly one child ol element",
                    )
                )

    return errors


def run(path: str | Path) -> list[ResultMessage]:
    """Run navigation document checks."""
    candidate = Path(path)
    errors: list[ResultMessage] = []

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

    # Validate TOC
    errors.extend(_validate_nav_toc(candidate, root))

    # Validate nav type
    errors.extend(_validate_nav_type(candidate, root))

    # Validate nav structure
    errors.extend(_validate_nav_structure(candidate, root))

    return errors
