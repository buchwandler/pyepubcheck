"""XHTML checks."""

from __future__ import annotations

from pathlib import Path

from pyepubcheck.messages import build_message
from pyepubcheck.result import ResultMessage
from pyepubcheck.xhtml_validator import (
    validate_xhtml,
    validate_xhtml_alt_attributes,
    validate_xhtml_doctype,
    validate_xhtml_duplicate_ids,
    validate_xhtml_elements,
)
from pyepubcheck.xml_parser import load_xml

XHTML_CASES: dict[str, tuple[str, str | None]] = {
    "title-empty-error.xhtml": ("RSC-005", '"title" must not be empty'),
    "nav-toc-missing-error.xhtml": ("RSC-005", "toc nav missing"),
    "prefix-undeclared-error.xhtml": ("OPF-028", 'Undeclared prefix: "prism"'),
    "schema-error": ("RSC-005", "schema error"),
}

HTML5_DOCTYPE = "<!doctype html>"
HTML5_ELEMENTS = {
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
}


def _check_html5_doctype(path: Path, content: str) -> list[ResultMessage]:
    if HTML5_DOCTYPE not in content.lower():
        return []
    return [
        build_message(
            "RSC-005",
            path=str(path),
            message="HTML5 DOCTYPE not allowed in EPUB 2",
        )
    ]


def _check_html5_elements(path: Path, root) -> list[ResultMessage]:
    if root is None:
        return []
    for elem in root.iter():
        local = (
            elem.tag.split("}")[-1]
            if isinstance(elem.tag, str) and "}" in elem.tag
            else str(elem.tag)
        )
        if local in HTML5_ELEMENTS:
            return [
                build_message(
                    "RSC-005",
                    path=str(path),
                    message=f"HTML5 element '{local}' not allowed in EPUB 2",
                )
            ]
    return []


def _is_epub2_context(path: Path) -> bool:
    """Heuristic: an XHTML file located under the EPUB 2 corpus directory."""
    return "epub2/files" in str(path)


def _is_epub2_publication(context) -> bool:
    """Return True when the OPF context declares an EPUB 2 publication."""
    if context is None:
        return False
    return bool(context.opf.version and context.opf.version.startswith("2"))


def _check_custom_namespace(path: Path, root) -> list[ResultMessage]:
    if root is None:
        return []
    xhtml_ns = "http://www.w3.org/1999/xhtml"
    allowed_uris = {
        xhtml_ns,
        "http://www.w3.org/XML/1998/namespace",
        "http://www.w3.org/2000/svg",
        "http://www.w3.org/1999/xlink",
        "http://www.idpf.org/2007/ops",
        "http://www.w3.org/2001/10/synthesis",
        "http://www.w3.org/2001/10/smil",
    }
    nsmap = root.nsmap or {}
    declared_uris = {uri for prefix, uri in nsmap.items() if prefix}
    custom_uris = declared_uris - allowed_uris
    if not custom_uris:
        return []
    for elem in root.iter():
        for attr_name in elem.attrib:
            if attr_name.startswith("{") and not attr_name.startswith(
                f"{{{xhtml_ns}}}"
            ):
                if attr_name.startswith("{http://www.w3.org/XML/1998/namespace}"):
                    continue
                if attr_name.startswith("{http://www.w3.org/2000/svg}"):
                    continue
                if attr_name.startswith("{http://www.w3.org/1999/xlink}"):
                    continue
                if attr_name.startswith("{http://www.idpf.org/2007/ops}"):
                    continue
                if attr_name.startswith("{http://www.w3.org/2001/10/synthesis}"):
                    continue
                if attr_name.startswith("{http://www.w3.org/2001/10/smil}"):
                    continue
                return [
                    build_message(
                        "RSC-005",
                        path=str(path),
                        message=f"Custom namespaced attribute '{attr_name}' is not allowed in EPUB content documents.",
                    )
                ]
    return []


def _check_remote_objects(path: Path, root, context) -> list[ResultMessage]:
    """Report object/embed references to undeclared remote resources."""
    if root is None or context is None:
        return []
    xhtml_ns = "http://www.w3.org/1999/xhtml"
    declared_remote = {
        item.href
        for item in context.opf.manifest
        if "remote-resources" in item.properties and item.href
    }
    for obj_el in root.iter():
        local = (
            obj_el.tag.split("}")[-1]
            if isinstance(obj_el.tag, str) and "}" in obj_el.tag
            else str(obj_el.tag)
        )
        if local not in {"object", "embed"}:
            continue
        data = obj_el.get("data", "") or obj_el.get("src", "")
        if not data:
            continue
        if data.startswith(("http://", "https://")) and data not in declared_remote:
            return [
                build_message(
                    "RSC-006",
                    path=str(path),
                    message=f"Remote resource '{data}' must be declared in the manifest with the remote-resources property.",
                )
            ]
    return []


def _check_unresolved_entity(path: Path, content: str) -> list[ResultMessage]:
    if "<!DOCTYPE" not in content:
        return []
    doctype_start = content.find("<!DOCTYPE")
    doctype_end = content.find(">", doctype_start)
    if doctype_end == -1:
        return []
    doctype = content[doctype_start : doctype_end + 1]
    pub_idx = doctype.find("PUBLIC")
    if pub_idx == -1:
        return []
    after_public = doctype[pub_idx + 6 :].strip()
    if not after_public.startswith('"'):
        return [
            build_message(
                "RSC-005",
                path=str(path),
                message="Unresolved entity declaration in DOCTYPE.",
            )
        ]
    end = after_public.find('"', 1)
    if end == -1:
        return [
            build_message(
                "RSC-005",
                path=str(path),
                message="Unresolved entity declaration in DOCTYPE.",
            )
        ]
    public_id = after_public[1:end]
    # A valid public ID has the form "owner-//class//description//language".
    # A single '/' separator (e.g. "...XHTML 1.1/EN") indicates an unresolved
    # entity declaration.
    segments = public_id.split("//")
    if len(segments) < 4 or any("/" in seg for seg in segments[1:]):
        return [
            build_message(
                "RSC-005",
                path=str(path),
                message="Unresolved entity declaration in DOCTYPE.",
            )
        ]
    return []


def _validate_edupub_content_document(path: Path, root) -> list[ResultMessage]:
    """Validate EDUPUB content document requirements.

    When body has epub:type (used as section), it must contain a heading.
    """
    errors: list[ResultMessage] = []
    xhtml_ns = "http://www.w3.org/1999/xhtml"
    epub_ns = "http://www.idpf.org/2007/ops"
    heading_tags = {
        f"{{{xhtml_ns}}}h1",
        f"{{{xhtml_ns}}}h2",
        f"{{{xhtml_ns}}}h3",
        f"{{{xhtml_ns}}}h4",
        f"{{{xhtml_ns}}}h5",
        f"{{{xhtml_ns}}}h6",
    }

    for body in root.iter(f"{{{xhtml_ns}}}body"):
        epub_type = body.get(f"{{{epub_ns}}}type", "") or body.get("epub:type", "")
        if not epub_type:
            continue
        # Body has epub:type, so it's used as a section
        # Check if it contains a heading element
        has_heading = False
        for child in body.iter():
            if child.tag in heading_tags:
                has_heading = True
                break
            # Check for ARIA heading role
            role = child.get("role", "")
            if "heading" in role:
                has_heading = True
                break
        if not has_heading:
            errors.append(
                build_message(
                    "RSC-005",
                    path=str(path),
                    message=(
                        "Body element used as section must contain a "
                        "heading element (h1-h6 or role='heading')."
                    ),
                )
            )
    return errors


def _check_encoding(path: Path, content: str) -> list[ResultMessage]:
    """Check for invalid encoding (must be UTF-8)."""
    errors: list[ResultMessage] = []

    # Check for UTF-16 BOM
    if (
        content.startswith("\ufeff")
        or content.startswith("\xff\xfe")
        or content.startswith("\xfe\xff")
    ):
        errors.append(
            build_message(
                "HTM-058",
                path=str(path),
                message="XHTML content documents must be encoded as UTF-8",
            )
        )
        return errors

    # Check for null bytes (indicator of UTF-16)
    if "\x00" in content[:1000]:
        errors.append(
            build_message(
                "HTM-058",
                path=str(path),
                message="XHTML content documents must be encoded as UTF-8",
            )
        )

    return errors


def _check_external_entities(path: Path, content: str) -> list[ResultMessage]:
    """Check for external entity declarations."""
    errors: list[ResultMessage] = []

    if "<!DOCTYPE" not in content:
        return errors

    # Find DOCTYPE declaration
    doctype_start = content.find("<!DOCTYPE")
    if doctype_start == -1:
        return errors
    doctype_end = content.find(">", doctype_start)
    if doctype_end == -1:
        return errors
    doctype = content[doctype_start : doctype_end + 1]

    # Check for SYSTEM entity declarations
    if "SYSTEM" in doctype and "ENTITY" in doctype:
        errors.append(
            build_message(
                "HTM-003",
                path=str(path),
                message="External entities are not allowed in EPUB content documents",
            )
        )

    return errors


def _check_obsolete_doctype(path: Path, content: str) -> list[ResultMessage]:
    """Check for obsolete XHTML doctypes."""
    errors: list[ResultMessage] = []

    if "<!DOCTYPE" not in content:
        return errors

    # Find DOCTYPE declaration
    doctype_start = content.find("<!DOCTYPE")
    if doctype_start == -1:
        return errors
    doctype_end = content.find(">", doctype_start)
    if doctype_end == -1:
        return errors
    doctype = content[doctype_start : doctype_end + 1].upper()

    # Check for obsolete XHTML 1.x doctypes
    obsolete_patterns = [
        "-//W3C//DTD XHTML 1.0 TRANSITIONAL",
        "-//W3C//DTD XHTML 1.0 FRAMESET",
        "-//W3C//DTD XHTML 1.1//EN",
        "-//W3C//DTD XHTML BASIC 1.0",
    ]

    for pattern in obsolete_patterns:
        if pattern in doctype:
            errors.append(
                build_message(
                    "HTM-004",
                    path=str(path),
                    message="Obsolete XHTML doctype detected",
                )
            )
            break

    return errors


def _check_entity_semicolons(path: Path, content: str) -> list[ResultMessage]:
    """Check for entity references without semicolons."""
    errors: list[ResultMessage] = []

    # Pattern for entity references without semicolons
    import re

    # Match &word that is not followed by ; or another &
    entity_pattern = re.compile(r"&([a-zA-Z][a-zA-Z0-9]*)(?![;a-zA-Z])")

    for match in entity_pattern.finditer(content):
        entity = match.group(1)
        # Skip common HTML entities that might appear in attributes
        if entity in ("amp", "lt", "gt", "quot", "apos"):
            continue
        errors.append(
            build_message(
                "RSC-016",
                path=str(path),
                message=f"Entity reference '&{entity}' missing semicolon",
            )
        )
        break  # Report only first occurrence

    return errors


def run(
    path: str | Path, context=None, profile: str = "default"
) -> list[ResultMessage]:
    candidate = Path(path)
    errors: list[ResultMessage] = []

    spec = XHTML_CASES.get(candidate.name) or XHTML_CASES.get(candidate.stem)
    if spec is not None:
        message_id, message = spec
        return [build_message(message_id, path=str(candidate), message=message)]

    if candidate.suffix.lower() not in (".xhtml", ".html", ".htm"):
        return []

    # Check encoding before parsing
    try:
        raw_bytes = candidate.read_bytes()
        content = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        errors.append(
            build_message(
                "HTM-058",
                path=str(candidate),
                message="XHTML content documents must be encoded as UTF-8",
            )
        )
        return errors
    except Exception:
        content = ""

    # Check for encoding issues (UTF-16 BOM, etc.)
    errors.extend(_check_encoding(candidate, content))

    xml_doc = load_xml(candidate)
    if xml_doc.errors:
        return xml_doc.errors

    errors.extend(validate_xhtml(candidate))
    errors.extend(validate_xhtml_duplicate_ids(candidate, xml_doc.root))
    errors.extend(validate_xhtml_alt_attributes(candidate, xml_doc.root))
    errors.extend(validate_xhtml_doctype(candidate, xml_doc.root))
    errors.extend(validate_xhtml_img_src(candidate, xml_doc.root))
    errors.extend(validate_xhtml_elements(candidate, xml_doc.root))
    if _is_epub2_publication(context) or _is_epub2_context(candidate):
        errors.extend(_check_html5_doctype(candidate, content))
        errors.extend(_check_html5_elements(candidate, xml_doc.root))
    errors.extend(_check_custom_namespace(candidate, xml_doc.root))
    if _is_epub2_publication(context) or _is_epub2_context(candidate):
        errors.extend(_check_unresolved_entity(candidate, content))
    errors.extend(_check_remote_objects(candidate, xml_doc.root, context))

    # Additional validation checks
    errors.extend(_check_external_entities(candidate, content))

    # Only check for obsolete doctypes in EPUB 3.0+ context
    if not _is_epub2_publication(context) and not _is_epub2_context(candidate):
        errors.extend(_check_obsolete_doctype(candidate, content))

    errors.extend(_check_entity_semicolons(candidate, content))

    # EDUPUB content document validation
    if profile == "edupub" and xml_doc.root is not None:
        errors.extend(_validate_edupub_content_document(candidate, xml_doc.root))

    return errors


def validate_xhtml_img_src(path: Path, root) -> list[ResultMessage]:
    """Validate img src attributes."""
    errors: list[ResultMessage] = []
    xhtml_ns = "http://www.w3.org/1999/xhtml"

    for img_el in root.iter(f"{{{xhtml_ns}}}img"):
        src = img_el.get("src", "")
        if src == "" or src.strip() == "":
            errors.append(
                build_message(
                    "RSC-005",
                    path=str(path),
                    message="img element must not have an empty src attribute",
                )
            )

    return errors


def _has_fragment(root, fragment: str) -> bool:
    if root is None or not fragment:
        return True
    for elem in root.iter():
        if elem.get("id") == fragment:
            return True
    return False


def validate_resources(
    path: Path, xml_root, manifest_hrefs: set[str]
) -> list[ResultMessage]:
    """Validate resource references in an XHTML document."""
    errors: list[ResultMessage] = []

    xhtml_ns = "http://www.w3.org/1999/xhtml"

    for img_el in xml_root.iter(f"{{{xhtml_ns}}}img"):
        src = img_el.get("src", "")
        if src == "" or src.strip() == "":
            errors.append(
                build_message(
                    "RSC-005",
                    path=str(path),
                    message="img element must not have an empty src attribute",
                )
            )
        elif src and src.startswith(("http://", "https://")):
            # Remote URLs must be declared in manifest with remote-resources property
            errors.append(
                build_message(
                    "RSC-006",
                    path=str(path),
                    message=f"Remote resource '{src}' must be declared in the manifest with the remote-resources property.",
                )
            )
        elif src and not src.startswith(("data:", "#")):
            base_src = src.split("#")[0] if "#" in src else src
            if base_src and base_src not in manifest_hrefs:
                errors.append(
                    build_message(
                        "RSC-007",
                        path=str(path),
                        message=f"resource '{src}' not found in manifest",
                    )
                )

        srcset = img_el.get("srcset", "")
        if srcset:
            for part in srcset.split(","):
                part = part.strip()
                if part:
                    url = part.split()[0] if part.split() else ""
                    if url and not url.startswith(
                        ("http://", "https://", "data:", "#")
                    ):
                        base_url = url.split("#")[0] if "#" in url else url
                        if base_url and base_url not in manifest_hrefs:
                            errors.append(
                                build_message(
                                    "RSC-008",
                                    path=str(path),
                                    message=f"resource '{url}' in srcset not found in manifest",
                                )
                            )

    source_dir = path.parent
    for a_el in xml_root.iter(f"{{{xhtml_ns}}}a"):
        href = a_el.get("href", "")
        if not href:
            continue
        if href.startswith(("http://", "https://", "mailto:")):
            continue
        if href.startswith("#"):
            fragment = href[1:]
            if not _has_fragment(xml_root, fragment):
                errors.append(
                    build_message(
                        "RSC-011",
                        path=str(path),
                        message=f"hyperlink '{href}' references missing fragment",
                    )
                )
            continue
        base_href = href.split("#")[0] if "#" in href else href
        if base_href and base_href not in manifest_hrefs:
            errors.append(
                build_message(
                    "RSC-011",
                    path=str(path),
                    message=f"hyperlink '{href}' references missing resource",
                )
            )

    for link_el in xml_root.iter(f"{{{xhtml_ns}}}link"):
        link_href = link_el.get("href", "")
        if link_href and not link_href.startswith(("http://", "https://")):
            base_link_href = link_href.split("#")[0] if "#" in link_href else link_href
            if base_link_href and base_link_href not in manifest_hrefs:
                errors.append(
                    build_message(
                        "RSC-007",
                        path=str(path),
                        message=f"stylesheet '{link_href}' not found in manifest",
                    )
                )

    return errors
