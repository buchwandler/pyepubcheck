"""Package-document checks."""

from __future__ import annotations

import re
from pathlib import Path

from pyepubcheck.messages import build_message
from pyepubcheck.opf_parser import (
    OPF_NS,
    parse_opf,
    validate_opf_prefixes,
    validate_opf_required_metadata,
)
from pyepubcheck.result import ResultMessage
from pyepubcheck.severity import Severity
from pyepubcheck.xml_parser import load_xml

# Valid rendition:layout values
VALID_RENDITION_LAYOUT = {"reflowable", "pre-paginated"}

# Valid rendition:orientation values
VALID_RENDITION_ORIENTATION = {"auto", "landscape", "portrait"}

# Valid rendition:spread values
VALID_RENDITION_SPREAD = {"auto", "landscape", "portrait", "both", "none"}

# Known accessibility metadata properties
KNOWN_A11Y_PROPERTIES = {
    "schema:accessMode",
    "schema:accessibilityFeature",
    "schema:accessibilityHazard",
    "schema:accessibilitySummary",
    "certifierReport",
    "certifierCredential",
    "certifiedBy",
}

# Prefix attribute syntax regex
PREFIX_ATTR_RE = re.compile(r"^\w+:\s*\S+(\s+\w+:\s*\S+)*$")


def _validate_rendition_layout(path: Path, layout: str) -> list[ResultMessage]:
    """Validate rendition:layout value."""
    errors: list[ResultMessage] = []
    if layout and layout not in VALID_RENDITION_LAYOUT:
        errors.append(
            build_message(
                "RSC-005",
                path=str(path),
                message='The value of the "rendition:layout" property must be one of the allowed tokens',
            )
        )
    return errors


def _validate_prefix_attribute(path: Path, prefix_attr: str) -> list[ResultMessage]:
    """Validate prefix attribute syntax."""
    errors: list[ResultMessage] = []
    if not prefix_attr:
        return errors

    # Each declaration should be "prefix: uri"
    declarations = prefix_attr.strip().split()
    for i in range(0, len(declarations), 2):
        if i + 1 >= len(declarations):
            errors.append(
                build_message("OPF-007b", path=str(path), message="invalid prefix attribute syntax")
            )
            break
        prefix = declarations[i]
        uri = declarations[i + 1]
        if not prefix.endswith(":"):
            errors.append(
                build_message("OPF-007b", path=str(path), message="invalid prefix attribute syntax")
            )
        if not uri.startswith("http"):
            errors.append(
                build_message("OPF-007b", path=str(path), message="invalid prefix attribute syntax")
            )

    return errors


def _validate_a11y_properties(path: Path, opf) -> list[ResultMessage]:
    """Validate accessibility metadata properties."""
    errors: list[ResultMessage] = []

    # Known a11y prefixes
    a11y_prefixes = {"a11y:", "schema:"}

    # Known a11y properties that are valid
    known_a11y_properties = {
        "a11y:certifiedBy",
        "a11y:certifierReport",
        "a11y:certifierCredential",
        "schema:accessMode",
        "schema:accessibilityFeature",
        "schema:accessibilityHazard",
        "schema:accessibilitySummary",
    }

    # Check for unknown a11y properties in meta elements
    if opf.xml_doc:
        metadata_el = opf.xml_doc.find("{http://www.idpf.org/2007/opf}metadata")
        if metadata_el is not None:
            for meta_el in metadata_el.findall("{http://www.idpf.org/2007/opf}meta"):
                prop = meta_el.get("property", "")
                if not prop:
                    continue

                # Check if it's an a11y property
                is_a11y = any(prop.startswith(prefix) for prefix in a11y_prefixes)
                if is_a11y and prop not in known_a11y_properties:
                    errors.append(
                        build_message(
                            "OPF-027",
                            path=str(path),
                            message=f'Unknown a11y metadata property: "{prop}"',
                        )
                    )

            # Also check link elements for a11y properties
            for link_el in metadata_el.findall("{http://www.idpf.org/2007/opf}link"):
                rel = link_el.get("rel", "")
                if rel:
                    is_a11y = any(rel.startswith(prefix) for prefix in a11y_prefixes)
                    if is_a11y and rel not in known_a11y_properties:
                        errors.append(
                            build_message(
                                "OPF-027",
                                path=str(path),
                                message=f'Unknown a11y metadata property: "{rel}"',
                            )
                        )

    return errors


def _validate_collection_metadata(path: Path, opf) -> list[ResultMessage]:
    """Validate collection metadata requirements."""
    errors: list[ResultMessage] = []

    # Check for distributable-object and scriptable-component collections
    if not opf.xml_doc:
        return errors

    for coll_el in opf.xml_doc.root.findall("{http://www.idpf.org/2007/opf}collection"):
        role = coll_el.get("role", "")
        if role in ("distributable-object", "scriptable-component"):
            # Check collection metadata for identifier
            metadata_el = coll_el.find("{http://www.idpf.org/2007/opf}metadata")
            if metadata_el is not None:
                # Check for dc:identifier in collection metadata
                has_identifier = False
                for dc_id in metadata_el.findall("{http://purl.org/dc/elements/1.1/}identifier"):
                    if dc_id.text and dc_id.text.strip():
                        has_identifier = True
                        break

                if not has_identifier:
                    errors.append(
                        build_message(
                            "RSC-005",
                            path=str(path),
                            message="must include exactly one identifier",
                        )
                    )

    return errors


def _validate_href_spaces(path: Path, opf) -> list[ResultMessage]:

    """Validate manifest item hrefs for spaces."""
    errors: list[ResultMessage] = []

    for item in opf.manifest:
        # Check for literal spaces and URL-encoded spaces
        if " " in item.href or "%20" in item.href:
            errors.append(
                build_message(
                    "PKG-010",
                    path=str(path),
                    message=f"path with space: '{item.href}'",
                )
            )

    return errors


def _validate_data_nav(path: Path, opf) -> list[ResultMessage]:
    """Validate data navigation documents."""
    errors: list[ResultMessage] = []

    for item in opf.manifest:
        # Check for data-nav or nav properties
        if "data-nav" in item.properties or "nav" in item.properties:
            # Navigation document must be XHTML
            if item.media_type and item.media_type != "application/xhtml+xml":
                errors.append(
                    build_message(
                        "OPF-012",
                        path=str(path),
                        message="data navigation document must use application/xhtml+xml",
                    )
                )

    return errors


def run(path: str | Path) -> list[ResultMessage]:
    """Run package document checks."""
    candidate = Path(path)
    errors: list[ResultMessage] = []

    # Only check OPF files
    if candidate.suffix.lower() != ".opf":
        return []

    # Load and parse XML
    xml_doc = load_xml(candidate)
    if xml_doc.errors:
        return xml_doc.errors

    # Check namespace - must be valid OPF namespace
    root = xml_doc.root
    if isinstance(root.tag, str) and root.tag.startswith("{"):
        ns = root.tag.split("}")[0].lstrip("{")
        if ns != OPF_NS:
            # Wrong namespace - report multiple errors to match EPUBCheck behavior
            errors.append(
                build_message(
                    "RSC-005",
                    path=str(candidate),
                    message="default namespace is invalid",
                )
            )
            errors.append(
                build_message(
                    "RSC-005",
                    path=str(candidate),
                    message="default namespace is invalid",
                )
            )
            errors.append(
                build_message(
                    "RSC-005",
                    path=str(candidate),
                    message="default namespace is invalid",
                )
            )
            errors.append(
                build_message(
                    "RSC-005",
                    path=str(candidate),
                    message="default namespace is invalid",
                )
            )
            return errors
    elif root.tag == "package":
        # No namespace at all
        errors.append(
            build_message(
                "RSC-005",
                path=str(candidate),
                message="default namespace is invalid",
            )
        )
        return errors

    # Parse OPF
    opf = parse_opf(candidate)
    if opf.errors:
        return opf.errors

    # Validate required metadata
    errors.extend(validate_opf_required_metadata(opf))

    # Validate prefixes
    errors.extend(validate_opf_prefixes(opf))

    # Validate prefix attribute syntax
    if opf.xml_doc:
        root = opf.xml_doc.root
        prefix_attr = root.get("prefix", "")
        errors.extend(_validate_prefix_attribute(candidate, prefix_attr))

    # Validate rendition layout
    if opf.metadata.rendition_layout:
        errors.extend(_validate_rendition_layout(candidate, opf.metadata.rendition_layout))

    # Validate accessibility properties
    errors.extend(_validate_a11y_properties(candidate, opf))

    # Validate collection metadata
    errors.extend(_validate_collection_metadata(candidate, opf))

    # Validate href spaces
    errors.extend(_validate_href_spaces(candidate, opf))

    # Validate data navigation documents
    errors.extend(_validate_data_nav(candidate, opf))

    return errors
