"""Media-overlay checks."""

from __future__ import annotations

from pathlib import Path

from pyepubcheck.messages import build_message
from pyepubcheck.result import ResultMessage
from pyepubcheck.xml_parser import load_xml

SMIL_NS = "{http://www.w3.org/ns/SMIL}"


def _validate_smil_structure(path: Path, root) -> list[ResultMessage]:
    """Validate SMIL document structure."""
    errors: list[ResultMessage] = []

    body = root.find(f"{SMIL_NS}body")
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

    head = root.find(f"{SMIL_NS}head")
    if head is not None:
        for child in head:
            if child.tag == f"{SMIL_NS}meta":
                errors.append(
                    build_message(
                        "RSC-005",
                        path=str(path),
                        message='element "meta" not allowed here',
                    )
                )

    return errors


def _validate_seq_children(path: Path, root) -> list[ResultMessage]:
    """Validate that seq elements only contain seq or par children."""
    errors: list[ResultMessage] = []

    for seq in root.iter(f"{SMIL_NS}seq"):
        for child in seq:
            tag = child.tag
            if not isinstance(tag, str):
                continue
            tag = tag.replace(SMIL_NS, "")
            if tag in ("text", "audio"):
                errors.append(
                    build_message(
                        "RSC-005",
                        path=str(path),
                        message=f'element "{tag}" not allowed here',
                    )
                )

    return errors


def _validate_par_children(path: Path, root) -> list[ResultMessage]:
    """Validate that par elements have at most one text child and no seq child."""
    errors: list[ResultMessage] = []

    for par in root.iter(f"{SMIL_NS}par"):
        text_count = 0
        child_count = 0
        for child in par:
            tag = child.tag
            if not isinstance(tag, str):
                continue
            tag = tag.replace(SMIL_NS, "")
            child_count += 1
            if tag == "text":
                text_count += 1
                if text_count > 1:
                    errors.append(
                        build_message(
                            "RSC-005",
                            path=str(path),
                            message='element "text" not allowed here',
                        )
                    )
            elif tag == "seq":
                errors.append(
                    build_message(
                        "RSC-005",
                        path=str(path),
                        message='element "seq" not allowed here',
                    )
                )
        if child_count == 0:
            errors.append(
                build_message(
                    "RSC-005",
                    path=str(path),
                    message="par element must have at least one text or audio child",
                )
            )

    return errors


def _validate_overlay_references(path: Path, root) -> list[ResultMessage]:
    """Validate media overlay references within a single file."""
    errors: list[ResultMessage] = []

    seen_refs: set[str] = set()
    for par in root.iter(f"{SMIL_NS}par"):
        text_ref = par.find(f"{SMIL_NS}text")
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


def check_cross_overlay_references(
    smil_paths: list[Path],
) -> list[ResultMessage]:
    """Check for content documents referenced from multiple overlay files.

    This is a cross-file check that must be called with all SMIL paths.
    """
    errors: list[ResultMessage] = []
    doc_to_smil: dict[str, list[str]] = {}

    for smil_path in smil_paths:
        xml_doc = load_xml(smil_path)
        if xml_doc.errors or xml_doc.root is None:
            continue
        if xml_doc.doc_type != "smil":
            continue

        for par in xml_doc.root.iter(f"{SMIL_NS}par"):
            text_ref = par.find(f"{SMIL_NS}text")
            if text_ref is not None:
                src = text_ref.get("src", "")
                # Normalize: strip fragment for cross-file comparison
                doc_ref = src.split("#")[0] if "#" in src else src
                if doc_ref:
                    doc_to_smil.setdefault(doc_ref, []).append(str(smil_path))

    for doc_ref, smil_files in doc_to_smil.items():
        if len(set(smil_files)) > 1:
            errors.append(
                build_message(
                    "MED-011",
                    path=smil_files[0],
                    message=(
                        f"content document referenced by multiple media overlays: "
                        f"'{doc_ref}'"
                    ),
                )
            )

    return errors


def run(path: str | Path) -> list[ResultMessage]:
    """Run media overlay checks."""
    candidate = Path(path)
    errors: list[ResultMessage] = []

    if candidate.suffix.lower() != ".smil":
        return []

    xml_doc = load_xml(candidate)
    if xml_doc.errors:
        return xml_doc.errors

    root = xml_doc.root

    if xml_doc.doc_type != "smil":
        return []

    errors.extend(_validate_smil_structure(candidate, root))
    errors.extend(_validate_smil_metadata(candidate, root))
    errors.extend(_validate_seq_children(candidate, root))
    errors.extend(_validate_par_children(candidate, root))
    errors.extend(_validate_overlay_references(candidate, root))

    return errors
