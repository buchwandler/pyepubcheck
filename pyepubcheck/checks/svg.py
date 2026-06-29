"""SVG checks."""

from __future__ import annotations

from pathlib import Path

from pyepubcheck.messages import build_message
from pyepubcheck.result import ResultMessage
from pyepubcheck.xml_parser import load_xml


def _validate_svg_use_href(path: Path, root) -> list[ResultMessage]:
    """Validate SVG use element href attributes."""
    errors: list[ResultMessage] = []

    # Find all use elements
    for use_el in root.iter("{http://www.w3.org/2000/svg}use"):
        href = use_el.get("href", "") or use_el.get(
            "{http://www.w3.org/1999/xlink}href", ""
        )
        if not href:
            continue

        # Check for fragment reference
        if "#" not in href:
            errors.append(
                build_message(
                    "RSC-015",
                    path=str(path),
                    message=f"SVG use element must target a fragment: '{href}'",
                )
            )

    return errors


def _validate_svg_ids(path: Path, root) -> list[ResultMessage]:
    """Validate SVG ID uniqueness."""
    errors: list[ResultMessage] = []
    seen_ids: set[str] = set()

    for el in root.iter():
        el_id = el.get("id")
        if el_id:
            if el_id in seen_ids:
                errors.append(
                    build_message(
                        "RSC-005",
                        path=str(path),
                        message=f"Duplicate ID: '{el_id}'",
                    )
                )
            else:
                seen_ids.add(el_id)

    return errors


def run(path: str | Path) -> list[ResultMessage]:
    """Run SVG content document checks."""
    candidate = Path(path)
    errors: list[ResultMessage] = []

    # Only check SVG files
    if candidate.suffix.lower() not in (".svg", ".xhtml", ".html"):
        return []

    # Load and parse XML
    xml_doc = load_xml(candidate)
    if xml_doc.errors:
        return xml_doc.errors

    root = xml_doc.root

    # Check if this is an SVG document
    if xml_doc.doc_type != "svg":
        return []

    # Validate use element hrefs
    errors.extend(_validate_svg_use_href(candidate, root))

    # Validate ID uniqueness
    errors.extend(_validate_svg_ids(candidate, root))

    return errors
