"""XHTML document validation."""

from __future__ import annotations

from pathlib import Path

from lxml import etree

from pyepubcheck.result import ResultMessage
from pyepubcheck.severity import Severity
from pyepubcheck.xml_parser import XHTML_NS, XmlDocument, load_xml


def validate_xhtml(path: Path | str) -> list[ResultMessage]:
    """Validate an XHTML document.

    Checks:
    - Well-formedness
    - Namespace declaration
    - Title element presence
    - Basic structure
    """
    file_path = Path(path)
    errors: list[ResultMessage] = []

    xml_doc = load_xml(file_path)
    if xml_doc.errors:
        return xml_doc.errors

    root = xml_doc.root
    ns = xml_doc.nsmap

    # Check XHTML namespace
    has_xhtml_ns = False
    for ns_uri in ns.values():
        if ns_uri == XHTML_NS:
            has_xhtml_ns = True
            break

    # Also check root tag directly
    if not has_xhtml_ns and isinstance(root.tag, str):
        if root.tag == "{http://www.w3.org/1999/xhtml}html" or root.tag == "html":
            has_xhtml_ns = True

    if not has_xhtml_ns:
        # Some EPUBs use html without explicit namespace
        if isinstance(root.tag, str) and root.tag.endswith("}html"):
            pass  # Has namespace, just not XHTML
        elif root.tag != "html":
            errors.append(
                ResultMessage(
                    id="RSC-005",
                    severity=Severity.ERROR,
                    message="XHTML document must use XHTML namespace",
                    path=str(file_path),
                )
            )

    # Check for title element
    title_el = root.find(".//{http://www.w3.org/1999/xhtml}title")
    if title_el is None:
        title_el = root.find(".//title")

    if title_el is not None:
        title_text = title_el.text
        if not title_text or not title_text.strip():
            errors.append(
                ResultMessage(
                    id="RSC-005",
                    severity=Severity.ERROR,
                    message='"title" must not be empty',
                    path=str(file_path),
                )
            )
    else:
        errors.append(
            ResultMessage(
                id="RSC-005",
                severity=Severity.ERROR,
                message="XHTML document must have a title element",
                path=str(file_path),
            )
        )

    # Check for required structure (html > head, body)
    html_el = root
    if isinstance(root.tag, str):
        local_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag
        if local_tag != "html":
            errors.append(
                ResultMessage(
                    id="RSC-005",
                    severity=Severity.ERROR,
                    message="Root element must be html",
                    path=str(file_path),
                )
            )

    return errors


def validate_xhtml_nav(doc: XmlDocument) -> list[ResultMessage]:
    """Validate XHTML navigation document.

    Checks for nav element with epub:type attribute.
    """
    errors: list[ResultMessage] = []
    path = str(doc.path)

    # Find nav elements
    nav_elements = doc.findall(".//{http://www.w3.org/1999/xhtml}nav")
    if not nav_elements:
        nav_elements = doc.findall(".//nav")

    if not nav_elements:
        errors.append(
            ResultMessage(
                id="RSC-005",
                severity=Severity.ERROR,
                message="Navigation document must contain at least one nav element",
                path=path,
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
            ResultMessage(
                id="RSC-005",
                severity=Severity.ERROR,
                message="toc nav missing",
                path=path,
            )
        )

    return errors


def validate_xhtml_title(doc: XmlDocument) -> list[ResultMessage]:
    """Validate XHTML title element."""
    errors: list[ResultMessage] = []
    path = str(doc.path)

    title_el = doc.find(".//{http://www.w3.org/1999/xhtml}title")
    if title_el is None:
        title_el = doc.find(".//title")

    if title_el is not None:
        title_text = title_el.text
        if not title_text or not title_text.strip():
            errors.append(
                ResultMessage(
                    id="RSC-005",
                    severity=Severity.ERROR,
                    message='"title" must not be empty',
                    path=path,
                )
            )
    else:
        errors.append(
            ResultMessage(
                id="RSC-005",
                severity=Severity.ERROR,
                message="XHTML document must have a title element",
                path=path,
            )
        )

    return errors


def validate_xhtml_duplicate_ids(path: Path | str, root) -> list[ResultMessage]:
    """Validate that no duplicate IDs exist in the document."""
    file_path = Path(path)
    errors: list[ResultMessage] = []

    # Collect all IDs
    id_counts: dict[str, int] = {}

    def collect_ids(element):
        elem_id = element.get("id", "")
        if elem_id:
            id_counts[elem_id] = id_counts.get(elem_id, 0) + 1
        for child in element:
            collect_ids(child)

    collect_ids(root)

    # Report duplicates
    for elem_id, count in id_counts.items():
        if count > 1:
            errors.append(
                ResultMessage(
                    id="RSC-005",
                    severity=Severity.ERROR,
                    message=f"duplicate ID '{elem_id}' found {count} times",
                    path=str(file_path),
                )
            )

    return errors


def validate_xhtml_alt_attributes(path: Path | str, root) -> list[ResultMessage]:
    """Validate that img elements have alt attributes."""
    file_path = Path(path)
    errors: list[ResultMessage] = []

    # Find all img elements
    xhtml_ns = "http://www.w3.org/1999/xhtml"
    for img_el in root.iter(f"{{{xhtml_ns}}}img"):
        alt = img_el.get("alt")
        if alt is None:
            errors.append(
                ResultMessage(
                    id="RSC-005",
                    severity=Severity.ERROR,
                    message="img element missing alt attribute",
                    path=str(file_path),
                )
            )

    return errors


def validate_xhtml_resource_references(path: Path | str, root, manifest_items: set[str]) -> list[ResultMessage]:
    """Validate that referenced resources exist in manifest."""
    file_path = Path(path)
    errors: list[ResultMessage] = []

    xhtml_ns = "http://www.w3.org/1999/xhtml"

    # Check img src attributes
    for img_el in root.iter(f"{{{xhtml_ns}}}img"):
        src = img_el.get("src", "")
        if src and not src.startswith(("http://", "https://", "data:", "#")):
            base_src = src.split("#")[0] if "#" in src else src
            if base_src and base_src not in manifest_items:
                errors.append(
                    ResultMessage(
                        id="RSC-007",
                        severity=Severity.ERROR,
                        message=f"referenced resource '{src}' not found in manifest",
                        path=str(file_path),
                    )
                )

    return errors


def validate_xhtml_style_elements(path: Path | str, root) -> list[ResultMessage]:
    """Validate style elements in XHTML."""
    file_path = Path(path)
    errors: list[ResultMessage] = []

    xhtml_ns = "http://www.w3.org/1999/xhtml"

    # Check for style elements
    for style_el in root.iter(f"{{{xhtml_ns}}}style"):
        # Check if style element has content
        if style_el.text and style_el.text.strip():
            # Style elements are allowed in EPUB 3
            pass

    return errors
