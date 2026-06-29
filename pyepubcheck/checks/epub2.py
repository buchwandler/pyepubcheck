"""EPUB 2 specific validation checks."""

from __future__ import annotations

import re
from pathlib import Path

from pyepubcheck.messages import build_message
from pyepubcheck.opf_parser import OPF_NS, parse_opf
from pyepubcheck.result import ResultMessage
from pyepubcheck.xml_parser import load_xml


def _validate_unique_identifier(path: Path, opf) -> list[ResultMessage]:
    """Validate that the unique-identifier attribute references a valid ID."""
    errors: list[ResultMessage] = []

    if not opf.xml_doc:
        return errors

    # Get the unique-identifier attribute from the package element
    root = opf.xml_doc.root
    unique_id_ref = root.get("unique-identifier", "")

    if not unique_id_ref:
        return errors

    # Check if the referenced ID exists in dc:identifier elements
    metadata_el = root.find(f"{{{OPF_NS}}}metadata")
    if metadata_el is None:
        return errors

    # Look for dc:identifier with the referenced ID
    dc_ns = "http://purl.org/dc/elements/1.1/"
    found = False
    for identifier_el in metadata_el.findall(f"{{{dc_ns}}}identifier"):
        if identifier_el.get("id", "") == unique_id_ref:
            found = True
            break

    if not found:
        errors.append(
            build_message(
                "OPF-030",
                path=str(path),
                message=f"unique-identifier '{unique_id_ref}' not found in dc:identifier elements",
            )
        )

    return errors


def _validate_spine_toc(path: Path, opf) -> list[ResultMessage]:
    """Validate spine toc attribute when NCX is present."""
    errors: list[ResultMessage] = []

    if not opf.xml_doc:
        return errors

    root = opf.xml_doc.root

    # Check if the root element has the correct namespace
    root_ns = root.tag.split("}")[0].lstrip("{") if "{" in root.tag else ""
    if root_ns != OPF_NS:
        # Wrong namespace - don't check spine
        return errors

    spine_el = root.find(f"{{{OPF_NS}}}spine")
    if spine_el is None:
        errors.append(
            build_message(
                "RSC-005",
                path=str(path),
                message="missing spine element",
            )
        )
        return errors

    toc_attr = spine_el.get("toc", "")
    if not toc_attr:
        # Check if there's an NCX in the manifest
        manifest_el = root.find(f"{{{OPF_NS}}}manifest")
        if manifest_el is not None:
            for item_el in manifest_el.findall(f"{{{OPF_NS}}}item"):
                media_type = item_el.get("media-type", "")
                if media_type == "application/x-dtbncx+xml":
                    errors.append(
                        build_message(
                            "OPF-003",
                            path=str(path),
                            message="NCX document found but spine toc attribute is missing",
                        )
                    )
                    break
        return errors

    # Check if the toc attribute points to a valid NCX
    manifest_el = root.find(f"{{{OPF_NS}}}manifest")
    if manifest_el is None:
        return errors

    ncx_found = False
    for item_el in manifest_el.findall(f"{{{OPF_NS}}}item"):
        item_id = item_el.get("id", "")
        media_type = item_el.get("media-type", "")
        if item_id.strip() == toc_attr.strip():
            if media_type != "application/x-dtbncx+xml":
                errors.append(
                    build_message(
                        "RSC-005",
                        path=str(path),
                        message=f"spine toc attribute '{toc_attr}' does not point to an NCX document",
                    )
                )
            ncx_found = True
            break

    if not ncx_found:
        errors.append(
            build_message(
                "RSC-005",
                path=str(path),
                message=f"spine toc attribute '{toc_attr}' references unknown manifest item",
            )
        )

    return errors


def _validate_manifest_items(path: Path, opf) -> list[ResultMessage]:
    """Validate manifest items exist and have valid references."""
    errors: list[ResultMessage] = []

    if not opf.xml_doc:
        return errors

    root = opf.xml_doc.root
    manifest_el = root.find(f"{{{OPF_NS}}}manifest")
    if manifest_el is None:
        return errors

    # Check each manifest item
    for item_el in manifest_el.findall(f"{{{OPF_NS}}}item"):
        item_id = item_el.get("id", "")
        href = item_el.get("href", "")
        media_type = item_el.get("media-type", "")

        # Validate required attributes
        if not item_id:
            errors.append(
                build_message(
                    "RSC-005",
                    path=str(path),
                    message="manifest item missing 'id' attribute",
                )
            )

        if not href:
            errors.append(
                build_message(
                    "RSC-007",
                    path=str(path),
                    message=f"manifest item '{item_id}' missing 'href' attribute",
                )
            )

        if not media_type:
            errors.append(
                build_message(
                    "RSC-005",
                    path=str(path),
                    message=f"manifest item '{item_id}' missing 'media-type' attribute",
                )
            )

    return errors


def _validate_fallbacks(path: Path, opf) -> list[ResultMessage]:
    """Validate manifest item fallbacks."""
    errors: list[ResultMessage] = []

    if not opf.xml_doc:
        return errors

    root = opf.xml_doc.root
    manifest_el = root.find(f"{{{OPF_NS}}}manifest")
    if manifest_el is None:
        return errors

    # Build a map of item IDs
    item_ids = set()
    for item_el in manifest_el.findall(f"{{{OPF_NS}}}item"):
        item_id = item_el.get("id", "")
        if item_id:
            item_ids.add(item_id)

    # Check fallback attributes
    for item_el in manifest_el.findall(f"{{{OPF_NS}}}item"):
        fallback = item_el.get("fallback", "")
        if fallback and fallback not in item_ids:
            errors.append(
                build_message(
                    "OPF-040",
                    path=str(path),
                    message=f"fallback '{fallback}' not found in manifest",
                )
            )

    return errors


def _validate_ncx_ids(path: Path, ncx_root) -> list[ResultMessage]:
    """Validate NCX document for duplicate and invalid IDs."""
    errors: list[ResultMessage] = []

    # XML ID syntax: must start with letter or underscore, followed by letters, digits, hyphens, underscores, or periods
    # Colons are not allowed in NCX IDs
    id_syntax_re = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_.\-]*$")

    # Collect all IDs in the NCX
    id_counts: dict[str, int] = {}

    def collect_ids(element):
        elem_id = element.get("id", "")
        if elem_id:
            # Check for invalid ID syntax
            if not id_syntax_re.match(elem_id):
                errors.append(
                    build_message(
                        "NCX-002",
                        path=str(path),
                        message=f"invalid NCX ID syntax '{elem_id}'",
                    )
                )
            id_counts[elem_id] = id_counts.get(elem_id, 0) + 1
        for child in element:
            collect_ids(child)

    collect_ids(ncx_root)

    # Report duplicates
    for elem_id, count in id_counts.items():
        if count > 1:
            errors.append(
                build_message(
                    "NCX-002",
                    path=str(path),
                    message=f"duplicate NCX ID '{elem_id}' found {count} times",
                )
            )

    return errors


def _validate_ncx_resources(
    path: Path, ncx_root, spine_items: set[str]
) -> list[ResultMessage]:
    """Validate NCX references to spine items."""
    errors: list[ResultMessage] = []

    # Find all navPoint elements and check their src attributes
    ncx_ns = "http://www.daisy.org/z3986/2005/ncx/"

    def check_navpoints(element):
        if element.tag == f"{{{ncx_ns}}}navPoint":
            # Look for content child with src attribute
            for child in element:
                if child.tag == f"{{{ncx_ns}}}content":
                    src = child.get("src", "")
                    if src:
                        # Extract the fragment if any
                        base_src = src.split("#")[0] if "#" in src else src
                        if base_src and base_src not in spine_items:
                            errors.append(
                                build_message(
                                    "NCX-003",
                                    path=str(path),
                                    message=f"NCX references '{src}' not found in spine",
                                )
                            )
        for child in element:
            check_navpoints(child)

    check_navpoints(ncx_root)

    return errors


def _validate_ncx_uid(path: Path, ncx_root, opf_uid: str) -> list[ResultMessage]:
    """Validate NCX UID matches OPF UID."""
    errors: list[ResultMessage] = []

    # Find the dtb:uid in the NCX head
    ncx_ns = "http://www.daisy.org/z3986/2005/ncx/"
    head_el = ncx_root.find(f"{{{ncx_ns}}}head")
    if head_el is None:
        return errors

    for meta_el in head_el.findall(f"{{{ncx_ns}}}meta"):
        if meta_el.get("name", "") == "dtb:uid":
            ncx_uid = meta_el.get("content", "").strip()
            opf_uid_stripped = opf_uid.strip()
            if ncx_uid and opf_uid_stripped and ncx_uid != opf_uid_stripped:
                errors.append(
                    build_message(
                        "NCX-004",
                        path=str(path),
                        message=f"NCX UID '{ncx_uid}' does not match OPF UID '{opf_uid_stripped}'",
                    )
                )
            break

    return errors


def _validate_xhtml_namespace(path: Path, xhtml_root) -> list[ResultMessage]:
    """Validate XHTML namespace in OPS content documents."""
    errors: list[ResultMessage] = []

    # Check for proper XHTML namespace
    if isinstance(xhtml_root.tag, str):
        if xhtml_root.tag.startswith("{"):
            ns = xhtml_root.tag.split("}")[0].lstrip("{")
            if ns != "http://www.w3.org/1999/xhtml":
                errors.append(
                    build_message(
                        "RSC-005",
                        path=str(path),
                        message=f"invalid XHTML namespace '{ns}'",
                    )
                )
        elif xhtml_root.tag == "html":
            # No namespace at all
            errors.append(
                build_message(
                    "RSC-005",
                    path=str(path),
                    message="XHTML document missing namespace declaration",
                )
            )

    return errors


def _validate_remote_objects(
    path: Path, xhtml_root, manifest_items: set[str]
) -> list[ResultMessage]:
    """Validate remote object references in XHTML."""
    errors: list[ResultMessage] = []

    # Check for references to external resources
    xhtml_ns = "http://www.w3.org/1999/xhtml"

    # Check img src attributes
    for img_el in xhtml_root.iter(f"{{{xhtml_ns}}}img"):
        src = img_el.get("src", "")
        if src and not src.startswith(("http://", "https://", "data:", "#")):
            # Local reference - check if it's in manifest
            base_src = src.split("#")[0] if "#" in src else src
            if base_src and base_src not in manifest_items:
                errors.append(
                    build_message(
                        "RSC-001",
                        path=str(path),
                        message=f"image '{src}' not declared in manifest",
                    )
                )

    return errors


def run_ncx(path: str | Path, opf_path: Path | None = None) -> list[ResultMessage]:
    """Run NCX-specific validation checks."""
    candidate = Path(path)
    errors: list[ResultMessage] = []

    # Only check NCX files
    if candidate.suffix.lower() != ".ncx":
        return []

    # Load and parse XML
    xml_doc = load_xml(candidate)
    if xml_doc.errors:
        return xml_doc.errors

    ncx_root = xml_doc.root
    if ncx_root is None:
        return errors

    # Validate duplicate IDs
    errors.extend(_validate_ncx_ids(candidate, ncx_root))

    # If we have an OPF path, we can do additional validation
    if opf_path and opf_path.exists():
        opf = parse_opf(opf_path)
        if not opf.errors and opf.xml_doc:
            root = opf.xml_doc.root
            spine_el = root.find(f"{{{OPF_NS}}}spine")
            if spine_el is not None:
                # Build set of spine item hrefs
                opf_dir = opf_path.parent
                spine_items: set[str] = set()
                manifest_el = root.find(f"{{{OPF_NS}}}manifest")
                if manifest_el is not None:
                    item_map: dict[str, str] = {}
                    for item_el in manifest_el.findall(f"{{{OPF_NS}}}item"):
                        item_id = item_el.get("id", "").strip()
                        href = item_el.get("href", "")
                        if item_id and href:
                            item_map[item_id] = href

                    # Get spine itemrefs
                    for itemref in spine_el.findall(f"{{{OPF_NS}}}itemref"):
                        idref = itemref.get("idref", "")
                        if idref in item_map:
                            href = item_map[idref]
                            # Resolve relative to OPF directory
                            resolved = (opf_dir / href).resolve()
                            spine_items.add(str(resolved))
                            # Also add just the href for relative matching
                            spine_items.add(href)

                # Validate NCX resources against spine
                errors.extend(_validate_ncx_resources(candidate, ncx_root, spine_items))

            # Get OPF UID for NCX UID validation
            dc_ns = "http://purl.org/dc/elements/1.1/"
            metadata_el = root.find(f"{{{OPF_NS}}}metadata")
            if metadata_el is not None:
                unique_id_ref = root.get("unique-identifier", "")
                if unique_id_ref:
                    for identifier_el in metadata_el.findall(f"{{{dc_ns}}}identifier"):
                        if identifier_el.get("id", "") == unique_id_ref:
                            opf_uid = identifier_el.text or ""
                            if opf_uid:
                                errors.extend(
                                    _validate_ncx_uid(candidate, ncx_root, opf_uid)
                                )
                            break

    return errors


def _validate_epub2_xhtml(path: Path) -> list[ResultMessage]:
    """EPUB 2 specific XHTML validation."""
    errors: list[ResultMessage] = []

    try:
        content = path.read_text(encoding="utf-8")
    except Exception:
        return errors

    # Check for HTML5 DOCTYPE
    if "<!doctype html>" in content.lower():
        errors.append(
            build_message(
                "RSC-005",
                path=str(path),
                message="HTML5 DOCTYPE not allowed in EPUB 2",
            )
        )

    # Check for HTML5 elements
    try:
        from lxml import etree

        tree = etree.parse(str(path))
        root = tree.getroot()
        html5_elements = [
            "article",
            "aside",
            "details",
            "figcaption",
            "figure",
            "footer",
            "header",
            "main",
            "mark",
            "nav",
            "section",
            "summary",
            "time",
        ]
        for elem in root.iter():
            local_name = (
                elem.tag.split("}")[-1] if "}" in str(elem.tag) else str(elem.tag)
            )
            if local_name in html5_elements:
                errors.append(
                    build_message(
                        "RSC-005",
                        path=str(path),
                        message=f"HTML5 element '{local_name}' not allowed in EPUB 2",
                    )
                )
                break
    except Exception:
        pass

    return errors


def run(path: str | Path) -> list[ResultMessage]:
    """Run EPUB 2 specific checks."""
    candidate = Path(path)
    errors: list[ResultMessage] = []

    # Only check OPF files
    if candidate.suffix.lower() != ".opf":
        return []

    # Load and parse XML
    xml_doc = load_xml(candidate)
    if xml_doc.errors:
        return xml_doc.errors

    # Parse OPF
    opf = parse_opf(candidate)
    if opf.errors:
        return opf.errors

    # Validate unique identifier
    errors.extend(_validate_unique_identifier(candidate, opf))

    # Validate spine toc
    errors.extend(_validate_spine_toc(candidate, opf))

    # Validate manifest items
    errors.extend(_validate_manifest_items(candidate, opf))

    # Validate fallbacks
    errors.extend(_validate_fallbacks(candidate, opf))

    # Validate XHTML files in manifest for EPUB 2 specific issues
    # Only apply EPUB 2 specific checks if version is 2.0
    if opf.version.startswith("2"):
        opf_dir = candidate.parent
        for item in opf.manifest:
            if item.media_type == "application/xhtml+xml" and item.href:
                item_path = opf_dir / item.href
                if item_path.exists():
                    errors.extend(_validate_epub2_xhtml(item_path))

    return errors
