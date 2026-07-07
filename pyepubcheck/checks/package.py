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
                build_message(
                    "OPF-007b",
                    path=str(path),
                    message="invalid prefix attribute syntax",
                )
            )
            break
        prefix = declarations[i]
        uri = declarations[i + 1]
        if not prefix.endswith(":"):
            errors.append(
                build_message(
                    "OPF-007b",
                    path=str(path),
                    message="invalid prefix attribute syntax",
                )
            )
        if not uri.startswith("http"):
            errors.append(
                build_message(
                    "OPF-007b",
                    path=str(path),
                    message="invalid prefix attribute syntax",
                )
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
                    for dc_id in metadata_el.findall(
                        "{http://purl.org/dc/elements/1.1/}identifier"
                    ):
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


def _validate_link_references(path: Path, opf) -> list[ResultMessage]:
    """Validate that link elements don't reference package document IDs."""
    errors: list[ResultMessage] = []
    if not opf.xml_doc:
        return errors

    # Build set of manifest item IDs
    manifest_ids = {item.id for item in opf.manifest if item.id}

    # Build set of all IDs in the document
    all_ids: set[str] = set()
    for elem in opf.xml_doc.root.iter():
        elem_id = elem.get("id", "")
        if elem_id:
            all_ids.add(elem_id)

    # Check link elements
    metadata_el = opf.xml_doc.find("{http://www.idpf.org/2007/opf}metadata")
    if metadata_el is not None:
        for link_el in metadata_el.findall("{http://www.idpf.org/2007/opf}link"):
            href = link_el.get("href", "")
            media_type = link_el.get("media-type", "")

            if not href:
                continue

            # Check if href references a package document ID (fragment reference)
            if href.startswith("#"):
                ref_id = href[1:]
                if ref_id in manifest_ids:
                    errors.append(
                        build_message(
                            "OPF-098",
                            path=str(path),
                            message=f"link target '{href}' must not reference a manifest ID",
                        )
                    )
                elif ref_id in all_ids:
                    # Link references a non-manifest ID in the package document
                    errors.append(
                        build_message(
                            "OPF-098",
                            path=str(path),
                            message=f"link target '{href}' must not reference a package document ID",
                        )
                    )
            elif not href.startswith(("http://", "https://", "mailto:")):
                # Local resource - must have media-type
                if not media_type:
                    errors.append(
                        build_message(
                            "OPF-098",
                            path=str(path),
                            message=f"local link '{href}' must have a media-type attribute",
                        )
                    )

    return errors


def _validate_unique_ids(path: Path, opf) -> list[ResultMessage]:
    """Validate that all ID attributes are unique."""
    errors: list[ResultMessage] = []
    if not opf.xml_doc:
        return errors

    # Collect all IDs and check for duplicates
    id_counts: dict[str, list[str]] = {}  # id -> list of element paths

    for elem in opf.xml_doc.root.iter():
        elem_id = elem.get("id", "")
        if not elem_id:
            continue

        # Build a simple path for the element
        tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
        if elem_id not in id_counts:
            id_counts[elem_id] = []
        id_counts[elem_id].append(tag)

    # Report duplicates
    for elem_id, locations in id_counts.items():
        if len(locations) > 1:
            errors.append(
                build_message(
                    "RSC-005",
                    path=str(path),
                    message=f"duplicate ID '{elem_id}' found in {', '.join(set(locations))}",
                )
            )

    return errors


def _validate_refines_references(path: Path, opf) -> list[ResultMessage]:
    """Validate refines attribute references."""
    errors: list[ResultMessage] = []
    if not opf.xml_doc:
        return errors

    # Build set of all IDs in the document
    all_ids: set[str] = set()
    for elem in opf.xml_doc.root.iter():
        elem_id = elem.get("id", "")
        if elem_id:
            all_ids.add(elem_id)

    # Check meta elements with refines attribute
    metadata_el = opf.xml_doc.find("{http://www.idpf.org/2007/opf}metadata")
    if metadata_el is not None:
        for meta_el in metadata_el.findall("{http://www.idpf.org/2007/opf}meta"):
            refines = meta_el.get("refines", "")
            if not refines:
                continue

            # Check for full URLs (not allowed)
            if refines.startswith(("http://", "https://")):
                errors.append(
                    build_message(
                        "RSC-005",
                        path=str(path),
                        message=f"refines attribute '{refines}' must be a relative URL",
                    )
                )
                continue

            # Check for non-fragment relative paths (warning)
            if not refines.startswith("#"):
                errors.append(
                    build_message(
                        "RSC-017",
                        path=str(path),
                        message=f"refines attribute '{refines}' should use a fragment ID",
                    )
                )
                continue

            # Check that the referenced ID exists
            ref_id = refines[1:]
            if ref_id not in all_ids:
                errors.append(
                    build_message(
                        "RSC-005",
                        path=str(path),
                        message=f"refines attribute references unknown ID '{ref_id}'",
                    )
                )

    # Check for refines cycles
    _check_refines_cycles(opf, errors, path)

    return errors


def _check_refines_cycles(opf, errors: list[ResultMessage], path: Path) -> None:
    """Check for cycles in refines references."""
    if not opf.xml_doc:
        return

    # Build refines graph
    refines_graph: dict[str, set[str]] = {}  # id -> set of ids it refines

    metadata_el = opf.xml_doc.find("{http://www.idpf.org/2007/opf}metadata")
    if metadata_el is None:
        return

    for meta_el in metadata_el.findall("{http://www.idpf.org/2007/opf}meta"):
        meta_id = meta_el.get("id", "")
        refines = meta_el.get("refines", "")
        if not meta_id or not refines or not refines.startswith("#"):
            continue

        target_id = refines[1:]
        if meta_id not in refines_graph:
            refines_graph[meta_id] = set()
        refines_graph[meta_id].add(target_id)

    # Check for cycles using DFS
    visited: set[str] = set()
    rec_stack: set[str] = set()

    def has_cycle(node: str) -> bool:
        visited.add(node)
        rec_stack.add(node)

        for neighbor in refines_graph.get(node, set()):
            if neighbor not in visited:
                if has_cycle(neighbor):
                    return True
            elif neighbor in rec_stack:
                return True

        rec_stack.discard(node)
        return False

    for node in refines_graph:
        if node not in visited:
            if has_cycle(node):
                errors.append(
                    build_message(
                        "OPF-065",
                        path=str(path),
                        message="refines references form a cycle",
                    )
                )
                break


def _validate_lang_attributes(path: Path, opf) -> list[ResultMessage]:
    """Validate xml:lang attributes."""
    errors: list[ResultMessage] = []
    if not opf.xml_doc:
        return errors

    for elem in opf.xml_doc.root.iter():
        lang = elem.get("{http://www.w3.org/XML/1998/namespace}lang", "")
        if not lang:
            continue

        # Check for leading/trailing whitespace
        if lang != lang.strip():
            errors.append(
                build_message(
                    "OPF-092",
                    path=str(path),
                    message=f"xml:lang attribute has leading/trailing whitespace: '{lang}'",
                )
            )

    return errors


def _validate_required_metadata(path: Path, opf) -> list[ResultMessage]:
    """Validate required metadata fields."""
    errors: list[ResultMessage] = []

    # Check for required metadata
    if not opf.metadata.identifiers:
        errors.append(
            build_message(
                "OPF-029",
                path=str(path),
                message="package must have a dc:identifier",
            )
        )

    if not opf.metadata.titles:
        errors.append(
            build_message(
                "OPF-029",
                path=str(path),
                message="package must have a dc:title",
            )
        )

    if not opf.metadata.languages:
        errors.append(
            build_message(
                "OPF-029",
                path=str(path),
                message="package must have a dc:language",
            )
        )

    # dcterms:modified is only required for EPUB 3.0+
    version = getattr(opf, "version", "3.0")
    if version and not version.startswith("2"):
        if not opf.metadata.modified:
            errors.append(
                build_message(
                    "OPF-029",
                    path=str(path),
                    message="package must have a dcterms:modified property",
                )
            )

    return errors


# Core media types that don't require fallbacks
CORE_MEDIA_TYPES = {
    # Images
    "image/gif",
    "image/jpeg",
    "image/png",
    "image/svg+xml",
    "image/webp",
    # Audio
    "audio/mpeg",
    "audio/mp4",
    "audio/opus",
    "audio/wav",
    "audio/wave",
    "audio/x-wav",
    "audio/ogg",
    # Video
    "video/webm",
    "video/mp4",
    "video/h264",
    "video/ogg",
    # Style
    "text/css",
    # Fonts
    "font/ttf",
    "font/otf",
    "font/woff",
    "font/woff2",
    "application/font-sfnt",
    "application/x-font-ttf",
    "application/vnd.ms-opentype",
    "application/font-woff",
    # Other
    "application/xhtml+xml",
    "application/javascript",
    "application/ecmascript",
    "text/javascript",
    "application/x-dtbncx+xml",
    "application/smil+xml",
    "application/pls+xml",
    "application/mathml+xml",
    "application/mathml-presentation+xml",
    "application/mathml-content+xml",
    # EPUB Dictionary
    "application/vnd.epub.search-key-map+xml",
}


def _validate_fallback_chains(path: Path, opf) -> list[ResultMessage]:
    """Validate that foreign resources have fallback attributes."""
    errors: list[ResultMessage] = []

    # Only check EPUB 3 publications
    if opf.version and opf.version.startswith("2"):
        return errors

    for item in opf.manifest:
        if not item.href:
            continue
        # Skip remote URLs
        if item.href.startswith(("http://", "https://")):
            continue
        # Check if this is a foreign resource (not a core media type)
        if item.media_type and item.media_type not in CORE_MEDIA_TYPES:
            # Foreign resources must have a fallback attribute
            if not item.fallback:
                errors.append(
                    build_message(
                        "RSC-005",
                        path=str(path),
                        message=f"foreign resource '{item.href}' with media type '{item.media_type}' must have a fallback",
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
        errors.extend(
            _validate_rendition_layout(candidate, opf.metadata.rendition_layout)
        )

    # Validate accessibility properties
    errors.extend(_validate_a11y_properties(candidate, opf))

    # Validate collection metadata
    errors.extend(_validate_collection_metadata(candidate, opf))

    # Validate href spaces
    errors.extend(_validate_href_spaces(candidate, opf))

    # Validate data navigation documents
    errors.extend(_validate_data_nav(candidate, opf))

    # Validate link references
    errors.extend(_validate_link_references(candidate, opf))

    # Validate unique IDs
    errors.extend(_validate_unique_ids(candidate, opf))

    # Validate refines references
    errors.extend(_validate_refines_references(candidate, opf))

    # Validate lang attributes
    errors.extend(_validate_lang_attributes(candidate, opf))

    # Validate required metadata
    errors.extend(_validate_required_metadata(candidate, opf))

    # Validate manifest resources
    errors.extend(_validate_manifest_resources(candidate, opf))

    # Validate fallback chains for foreign resources
    errors.extend(_validate_fallback_chains(candidate, opf))

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
        # Skip remote URLs (http/https) - they are not local files
        if item.href.startswith(("http://", "https://")):
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
            errors.append(
                build_message(
                    "RSC-005",
                    path=str(path),
                    message="spine itemref missing 'idref' attribute",
                )
            )
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
