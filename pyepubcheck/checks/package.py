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
        "a11y:exemption",
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
                # Only require dc:identifier for distributable-object collections
                if role == "distributable-object":
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

    # Check for multiple data-nav files
    data_nav_items = [item for item in opf.manifest if "data-nav" in item.properties]
    if len(data_nav_items) > 1:
        errors.append(
            build_message(
                "RSC-005",
                path=str(path),
                message="The manifest must not include more than one Data Navigation Document",
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
    is_legacy = False
    if isinstance(root.tag, str) and root.tag.startswith("{"):
        ns = root.tag.split("}")[0].lstrip("{")
        if ns != OPF_NS:
            # Check for legacy OEBPS namespace
            legacy_ns = "http://openebook.org/namespaces/oeb-package/1.0/"
            if ns == legacy_ns:
                is_legacy = True
            else:
                # Unknown namespace - report multiple errors
                for _ in range(4):
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

    if is_legacy:
        # For legacy OEBPS 1.2, report deprecation warning
        errors.append(
            build_message(
                "OPF-086",
                path=str(candidate),
                message="legacy OEBPS package format",
            )
        )
        # Check legacy media types (warning only)
        for item in opf.manifest:
            if item.media_type in ("text/x-oeb1-document", "text/html", "text/css"):
                errors.append(
                    build_message(
                        "OPF-086",
                        path=str(candidate),
                        message=f"legacy media type '{item.media_type}'",
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

    # Validate manifest resources
    errors.extend(_validate_manifest_resources(candidate, opf))

    # Validate spine itemrefs
    errors.extend(_validate_spine_itemrefs(candidate, opf))

    # Validate version
    errors.extend(_validate_version(candidate, opf))

    # Validate guide references
    errors.extend(_validate_guide_references(candidate, opf))

    # Validate page-map
    errors.extend(_validate_pagemap(candidate, opf))

    # Check for deprecated media types in non-legacy OPFs
    if not is_legacy:
        for item in opf.manifest:
            if item.media_type in ("text/x-oeb1-document", "text/html"):
                errors.append(
                    build_message(
                        "OPF-086",
                        path=str(candidate),
                        message=f"legacy media type '{item.media_type}'",
                    )
                )

    return errors


def _validate_manifest_resources(path: Path, opf) -> list[ResultMessage]:
    """Validate that manifest items have valid resources."""
    errors: list[ResultMessage] = []
    if not opf.xml_doc:
        return errors

    # Only check resource existence when the OPF is inside an EPUB directory
    # Find the EPUB root by looking for META-INF/container.xml
    opf_dir = path.parent
    epub_root = None
    check_dir = opf_dir
    for _ in range(10):  # limit depth to avoid infinite loops
        if (check_dir / "META-INF" / "container.xml").exists():
            epub_root = check_dir
            break
        parent = check_dir.parent
        if parent == check_dir:
            break
        check_dir = parent
    if epub_root is None:
        return errors

    for item in opf.manifest:
        if not item.href:
            continue
        # Resolve the resource path (URL-decode the href)
        from urllib.parse import unquote
        decoded_href = unquote(item.href)
        resource_path = opf_dir / decoded_href
        if not resource_path.exists():
            errors.append(
                build_message(
                    "RSC-001",
                    path=str(path),
                    message=f"resource '{item.href}' not found",
                )
            )

    return errors


def _validate_spine_itemrefs(path: Path, opf) -> list[ResultMessage]:
    """Validate spine itemrefs for duplicates and missing references."""
    errors: list[ResultMessage] = []
    if not opf.xml_doc:
        return errors

    root = opf.xml_doc.root
    spine_el = root.find(f"{{{OPF_NS}}}spine")
    if spine_el is None:
        return errors

    # Build set of manifest item IDs
    manifest_ids = {item.id for item in opf.manifest}

    # Build set of data-nav item IDs
    data_nav_ids = {item.id for item in opf.manifest if "data-nav" in item.properties}

    # Check for repeated itemrefs
    seen_refs: set[str] = set()
    for itemref in spine_el.findall(f"{{{OPF_NS}}}itemref"):
        idref = itemref.get("idref", "")
        if not idref:
            continue

        # Check if idref references a manifest item
        # Note: IDs should not have spaces, but we handle them for robustness
        manifest_ids_stripped = {mid.strip() for mid in manifest_ids}
        if idref not in manifest_ids and idref not in manifest_ids_stripped:
            errors.append(
                build_message(
                    "RSC-005",
                    path=str(path),
                    message=f"spine itemref '{idref}' not found in manifest",
                )
            )

        # Check for data-nav in spine
        if idref in data_nav_ids:
            errors.append(
                build_message(
                    "OPF-087",
                    path=str(path),
                    message=f"data nav item '{idref}' included in spine",
                )
            )

        # Check for duplicates
        if idref in seen_refs:
            errors.append(
                build_message(
                    "OPF-003",
                    path=str(path),
                    message=f"spine itemref '{idref}' is repeated",
                )
            )
        else:
            seen_refs.add(idref)

    return errors


def _validate_version(path: Path, opf) -> list[ResultMessage]:
    """Validate package version attribute."""
    errors: list[ResultMessage] = []
    if not opf.xml_doc:
        return errors

    root = opf.xml_doc.root
    version = root.get("version", "")
    if not version:
        errors.append(
            build_message(
                "OPF-001",
                path=str(path),
                message="missing version attribute",
            )
        )

    return errors


def _validate_guide_references(path: Path, opf) -> list[ResultMessage]:
    """Validate guide references."""
    errors: list[ResultMessage] = []
    if not opf.xml_doc:
        return errors

    root = opf.xml_doc.root
    guide_el = root.find(f"{{{OPF_NS}}}guide")
    if guide_el is None:
        return errors

    # Build set of manifest item hrefs
    manifest_hrefs = {item.href for item in opf.manifest}

    for ref_el in guide_el.findall(f"{{{OPF_NS}}}reference"):
        href = ref_el.get("href", "")
        if not href:
            continue

        # Check if href references a manifest item
        base_href = href.split("#")[0] if "#" in href else href
        if base_href and base_href not in manifest_hrefs:
            errors.append(
                build_message(
                    "OPF-089",
                    path=str(path),
                    message=f"guide reference '{href}' not found in manifest",
                )
            )

        # Check if reference is to an image
        ref_type = ref_el.get("type", "")
        if ref_type and ref_type.lower() in ("cover", "title-page"):
            if href.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".svg")):
                errors.append(
                    build_message(
                        "OPF-089",
                        path=str(path),
                        message=f"guide reference '{href}' points to an image",
                    )
                )

    return errors


def _validate_pagemap(path: Path, opf) -> list[ResultMessage]:
    """Validate page-map attribute."""
    errors: list[ResultMessage] = []
    if not opf.xml_doc:
        return errors

    root = opf.xml_doc.root
    spine_el = root.find(f"{{{OPF_NS}}}spine")
    if spine_el is None:
        return errors

    page_map = spine_el.get("page-map", "")
    if not page_map:
        return errors

    # Build set of manifest item IDs
    manifest_ids = {item.id for item in opf.manifest}

    # Check if the page-map ID references a valid manifest item
    if page_map not in manifest_ids:
        errors.append(
            build_message(
                "OPF-037",
                path=str(path),
                message=f"page-map '{page_map}' not found in manifest",
            )
        )
    else:
        # Find the referenced item and check its media type
        for item in opf.manifest:
            if item.id == page_map:
                if item.media_type != "application/oebps-page-map+xml":
                    errors.append(
                        build_message(
                            "OPF-003",
                            path=str(path),
                            message=f"page-map '{page_map}' has invalid media type",
                        )
                    )
                break
    return errors
