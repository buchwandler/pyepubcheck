"""Navigation-document checks."""

from __future__ import annotations

from pathlib import Path

from pyepubcheck.messages import build_message
from pyepubcheck.result import ResultMessage
from pyepubcheck.xml_parser import load_xml


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
            ol_children = [el for el in nav if str(el.tag).endswith("}ol") or str(el.tag) == "ol"]
            if len(ol_children) != 1:
                errors.append(
                    build_message(
                        "RSC-005",
                        path=str(path),
                        message="A region-based nav element must contain exactly one child ol element",
                    )
                )
                continue

            # Validate content model of the ol element
            ol = ol_children[0]
            errors.extend(_validate_region_nav_ol(path, ol))

    # Check for region-based nav on non-nav elements
    for element in root.iter("{http://www.w3.org/1999/xhtml}*"):
        epub_type = element.get("{http://www.idpf.org/2007/ops}type", "")
        if not epub_type:
            epub_type = element.get("epub:type", "")

        if "region-based" in epub_type:
            # Check if element is a nav element
            tag = str(element.tag)
            if not tag.endswith("}nav") and tag != "nav":
                errors.append(
                    build_message(
                        "HTM-052",
                        path=str(path),
                        message="region-based navigation not defined on a nav element",
                    )
                )

    return errors


def _validate_region_nav_ol(path: Path, ol) -> list[ResultMessage]:
    """Validate the content model of a region-based nav ol element."""
    errors: list[ResultMessage] = []

    for li in ol:
        tag = str(li.tag)
        if not tag.endswith("}li") and tag != "li":
            continue

        # Get the children of the li element
        children = list(li)
        if not children:
            errors.append(
                build_message(
                    "RSC-005",
                    path=str(path),
                    message='The first child of a region-based nav list item must be either an "a" or "span" element',
                )
            )
            continue

        first_child = children[0]
        first_tag = str(first_child.tag)

        # Check first child is a or span
        if not (first_tag.endswith("}a") or first_tag == "a" or first_tag.endswith("}span") or first_tag == "span"):
            errors.append(
                build_message(
                    "RSC-005",
                    path=str(path),
                    message='The first child of a region-based nav list item must be either an "a" or "span" element',
                )
            )
            continue

        # Check if first child is a span
        if first_tag.endswith("}span") or first_tag == "span":
            # Span must contain exactly two a elements
            a_children = [el for el in first_child if str(el.tag).endswith("}a") or str(el.tag) == "a"]
            if len(a_children) != 2:
                errors.append(
                    build_message(
                        "RSC-005",
                        path=str(path),
                        message='"span" elements in region-base navs must contain exactly two "a" elements',
                    )
                )

        # Check if first child is an a element with text content
        if first_tag.endswith("}a") or first_tag == "a":
            if first_child.text and first_child.text.strip():
                errors.append(
                    build_message(
                        "RSC-017",
                        path=str(path),
                        message='"a" elements in region-based navs should not contain text labels',
                    )
                )

        # Check remaining children
        remaining = children[1:]
        if remaining:
            # After the first child, there can only be a single ol element
            if len(remaining) > 1:
                errors.append(
                    build_message(
                        "RSC-005",
                        path=str(path),
                        message=(
                            "The first child of a region-based nav list item can only be "
                            'followed by a single "ol" element',
                        ),
                    )
                )
            elif remaining:
                remaining_tag = str(remaining[0].tag)
                if not (remaining_tag.endswith("}ol") or remaining_tag == "ol"):
                    errors.append(
                        build_message(
                            "RSC-005",
                            path=str(path),
                            message=(
                                "The first child of a region-based nav list item can only be "
                                'followed by a single "ol" element',
                            ),
                        )
                    )

    return errors


def _validate_nav_content_model(path: Path, root) -> list[ResultMessage]:
    """Validate navigation document content model."""
    errors: list[ResultMessage] = []
    xhtml_ns = "http://www.w3.org/1999/xhtml"
    epub_ns = "http://www.idpf.org/2007/ops"

    for nav in root.iter(f"{{{xhtml_ns}}}nav"):
        epub_type = nav.get(f"{{{epub_ns}}}type", "") or nav.get("epub:type", "")
        if "toc" not in epub_type:
            continue

        # Check for p elements used as headings (direct child of nav, before ol)
        has_heading = False
        for child in nav:
            tag = str(child.tag)
            local_tag = tag.split("}")[-1] if "}" in tag else tag

            # Check if this is a heading element
            if local_tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
                has_heading = True
                # Check for empty headings
                if _is_empty_or_blank(child):
                    errors.append(
                        build_message(
                            "RSC-005",
                            path=str(path),
                            message="Navigation heading must not be empty",
                        )
                    )

                # Check for p elements inside headings
                for _p in child.iter(f"{{{xhtml_ns}}}p"):
                    errors.append(
                        build_message(
                            "RSC-005",
                            path=str(path),
                            message="Heading elements must not contain p elements",
                        )
                    )
                    break

            # Check for p elements used as headings (not inside h1-h6)
            elif local_tag == "p" and not has_heading:
                # This p element is used as a heading, which is not allowed
                errors.append(
                    build_message(
                        "RSC-005",
                        path=str(path),
                        message="Navigation heading must use a heading element (h1-h6)",
                    )
                )
                break

        # Check list items
        for ol in nav.iter(f"{{{xhtml_ns}}}ol"):
            errors.extend(_validate_nav_list_items(path, ol))

    return errors


def _is_empty_or_blank(element) -> bool:
    """Check if an element is empty or contains only whitespace."""
    text = element.text or ""
    if text.strip():
        return False
    # Check children
    for child in element:
        child_text = child.text or ""
        if child_text.strip():
            return False
        # Check tail
        if child.tail and child.tail.strip():
            return False
    return True


def _validate_nav_list_items(path: Path, ol) -> list[ResultMessage]:
    """Validate navigation list items."""
    errors: list[ResultMessage] = []

    for li in ol:
        tag = str(li.tag)
        if not tag.endswith("}li") and tag != "li":
            continue

        # Get direct children
        children = list(li)

        # Check if li has a label (a or span)
        has_link = False
        has_span = False
        has_nested_ol = False
        label_element = None

        for child in children:
            child_tag = str(child.tag)
            local_tag = child_tag.split("}")[-1] if "}" in child_tag else child_tag

            if local_tag == "a":
                has_link = True
                label_element = child
            elif local_tag == "span":
                has_span = True
                label_element = child
            elif local_tag == "ol":
                has_nested_ol = True

        # Leaf items (no nested ol) must have a link, not just a span
        if not has_nested_ol:
            if not has_link and not has_span:
                errors.append(
                    build_message(
                        "RSC-005",
                        path=str(path),
                        message="Leaf list item must have a link or span label",
                    )
                )
            elif has_span and not has_link:
                # Span without link and without nested ol is an error
                errors.append(
                    build_message(
                        "RSC-005",
                        path=str(path),
                        message="Leaf list item with span label must have a nested ol",
                    )
                )
            continue

        # Non-leaf items must have a label
        if not has_link and not has_span:
            errors.append(
                build_message(
                    "RSC-005",
                    path=str(path),
                    message="List item with nested list must have a label",
                )
            )
            continue

        # Check if label is empty
        if label_element is not None:
            if _is_label_empty(label_element):
                errors.append(
                    build_message(
                        "RSC-005",
                        path=str(path),
                        message="List item label must not be empty",
                    )
                )

    return errors


def _is_label_empty(element) -> bool:
    """Check if a label element (a or span) is empty or whitespace-only."""
    text = element.text or ""
    if text.strip():
        return False

    # Check for img elements
    for child in element:
        child_tag = str(child.tag)
        local_tag = child_tag.split("}")[-1] if "}" in child_tag else child_tag
        if local_tag == "img":
            return False
        # Check child text
        child_text = child.text or ""
        if child_text.strip():
            return False

    return True


def run(path: str | Path, *, is_data_nav: bool = False) -> list[ResultMessage]:
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
    for _nav in root.iter("{http://www.w3.org/1999/xhtml}nav"):
        is_nav = True
        break

    if not is_nav:
        return []

    # Validate TOC (only for regular nav documents, not data-nav)
    if not is_data_nav:
        errors.extend(_validate_nav_toc(candidate, root))

    # Validate nav type
    errors.extend(_validate_nav_type(candidate, root))

    # Validate nav structure
    errors.extend(_validate_nav_structure(candidate, root))

    # Validate nav content model
    errors.extend(_validate_nav_content_model(candidate, root))

    return errors
