"""Media-overlay checks."""

from __future__ import annotations

from pathlib import Path

from pyepubcheck.messages import build_message
from pyepubcheck.result import ResultMessage
from pyepubcheck.xml_parser import load_xml


def _validate_smil_structure(path: Path, root) -> list[ResultMessage]:
    """Validate SMIL document structure."""
    errors: list[ResultMessage] = []

    # Check for required elements
    body = root.find("{http://www.w3.org/ns/SMIL}body")
    if body is None:
        errors.append(
            build_message(
                "RSC-005",
                path=str(path),
                message="SMIL document must have a body element",
            )
        )

    return errors


def _validate_smil_metadata(path: Path, root) -> list[ResultMessage]:
    """Validate SMIL metadata."""
    errors: list[ResultMessage] = []

    # Find head element
    head = root.find("{http://www.w3.org/ns/SMIL}head")
    if head is not None:
        # Check for meta elements directly in head (should be in metadata)
        for child in head:
            if child.tag == "{http://www.w3.org/ns/SMIL}meta":
                errors.append(
                    build_message(
                        "RSC-005",
                        path=str(path),
                        message='element "meta" not allowed here',
                    )
                )

    return errors

    return errors


def _validate_overlay_references(path: Path, root) -> list[ResultMessage]:
    """Validate media overlay references."""
    errors: list[ResultMessage] = []

    # Check for multiple overlay references
    seen_refs: set[str] = set()
    for par in root.iter("{http://www.w3.org/ns/SMIL}par"):
        text_ref = par.find("{http://www.w3.org/ns/SMIL}text")
        if text_ref is not None:
            src = text_ref.get("src", "")
            if src in seen_refs:
                errors.append(
                    build_message(
                        "MED-011",
                        path=str(path),
                        message=f"content document referenced by multiple media overlays: '{src}'",
                    )
                )
            else:
                seen_refs.add(src)

    return errors


def run(path: str | Path) -> list[ResultMessage]:
    """Run media overlay checks."""
    candidate = Path(path)
    errors: list[ResultMessage] = []

    # Only check SMIL files
    if candidate.suffix.lower() != ".smil":
        return []

    # Load and parse XML
    xml_doc = load_xml(candidate)
    if xml_doc.errors:
        return xml_doc.errors

    root = xml_doc.root

    # Check if this is a SMIL document
    if xml_doc.doc_type != "smil":
        return []

    # Validate SMIL structure
    errors.extend(_validate_smil_structure(candidate, root))

    # Validate SMIL metadata
    errors.extend(_validate_smil_metadata(candidate, root))

    # Validate overlay references
    errors.extend(_validate_overlay_references(candidate, root))

    return errors
