"""Fixed-layout checks."""

from __future__ import annotations

from pathlib import Path

from pyepubcheck.messages import build_message
from pyepubcheck.opf_parser import parse_opf
from pyepubcheck.result import ResultMessage
from pyepubcheck.xml_parser import load_xml

# Valid rendition:layout values
VALID_LAYOUTS = {"reflowable", "pre-paginated"}

# Valid rendition:orientation values
VALID_ORIENTATIONS = {"auto", "landscape", "portrait"}

# Valid rendition:spread values
VALID_SPREADS = {"auto", "landscape", "portrait", "both", "none"}


def _validate_rendition_layout(path: Path, layout: str) -> list[ResultMessage]:
    """Validate rendition:layout value."""
    errors: list[ResultMessage] = []
    if layout and layout not in VALID_LAYOUTS:
        errors.append(
            build_message(
                "RSC-005",
                path=str(path),
                message='The value of the "rendition:layout" property must be one of the allowed tokens',
            )
        )
    return errors


def _validate_rendition_orientation(path: Path, orientation: str) -> list[ResultMessage]:
    """Validate rendition:orientation value."""
    errors: list[ResultMessage] = []
    if orientation and orientation not in VALID_ORIENTATIONS:
        errors.append(
            build_message(
                "RSC-005",
                path=str(path),
                message='The value of the "rendition:orientation" property must be one of the allowed tokens',
            )
        )
    return errors


def _validate_rendition_spread(path: Path, spread: str) -> list[ResultMessage]:
    """Validate rendition:spread value."""
    errors: list[ResultMessage] = []
    if spread and spread not in VALID_SPREADS:
        errors.append(
            build_message(
                "RSC-005",
                path=str(path),
                message='The value of the "rendition:spread" property must be one of the allowed tokens',
            )
        )
    return errors


def _validate_prefix_declarations(path: Path, opf) -> list[ResultMessage]:
    """Validate prefix declarations in OPF."""
    errors: list[ResultMessage] = []

    # Check for invalid prefix syntax
    if opf.xml_doc:
        root = opf.xml_doc.root
        prefix_attr = root.get("prefix", "")
        if prefix_attr:
            # Each declaration should be "prefix: uri"
            declarations = prefix_attr.strip().split()
            for i in range(0, len(declarations), 2):
                if i + 1 >= len(declarations):
                    errors.append(
                        build_message(
                            "OPF-007b",
                            path=str(path),
                            message="invalid prefix attribute syntax",
                        )
                    )
                    break
                prefix = declarations[i]
                if not prefix.endswith(":"):
                    errors.append(
                        build_message(
                            "OPF-007b",
                            path=str(path),
                            message="invalid prefix attribute syntax",
                        )
                    )

    return errors


def run(path: str | Path) -> list[ResultMessage]:
    """Run layout checks."""
    candidate = Path(path)
    errors: list[ResultMessage] = []

    # Only check OPF files
    if candidate.suffix.lower() != ".opf":
        return []

    # Load and parse XML
    xml_doc = load_xml(candidate)
    if xml_doc.errors:
        return xml_doc.errors

    # Check if this is an OPF document
    if xml_doc.doc_type != "opf":
        return []

    # Parse OPF
    opf = parse_opf(candidate)
    if opf.errors:
        return opf.errors

    # Validate rendition properties
    if opf.metadata.rendition_layout:
        errors.extend(_validate_rendition_layout(candidate, opf.metadata.rendition_layout))

    if opf.metadata.rendition_orientation:
        errors.extend(_validate_rendition_orientation(candidate, opf.metadata.rendition_orientation))

    if opf.metadata.rendition_spread:
        errors.extend(_validate_rendition_spread(candidate, opf.metadata.rendition_spread))

    # Validate prefix declarations
    errors.extend(_validate_prefix_declarations(candidate, opf))

    return errors
