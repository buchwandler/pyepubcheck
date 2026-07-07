"""EDUPUB profile checks.

Self-gates on the CLI-requested profile (or the OPF metadata). When the
``edupub`` profile is requested, the publication must declare an
``edupub`` dc:type and a navigation document with both ``toc`` and
``page-list`` semantics.
"""

from __future__ import annotations

from pathlib import Path

from pyepubcheck.checks.profiles import ProfileContext, is_profile_active
from pyepubcheck.messages import build_message
from pyepubcheck.result import ResultMessage
from pyepubcheck.xml_parser import load_xml


def _find_nav_with_type(nav_path, nav_type: str) -> bool:
    xml_doc = load_xml(nav_path)
    if xml_doc.errors or xml_doc.root is None:
        return False
    xhtml_ns = "http://www.w3.org/1999/xhtml"
    epub_ns = "http://www.idpf.org/2007/ops"
    for nav in xml_doc.root.iter(f"{{{xhtml_ns}}}nav"):
        epub_type = nav.get(f"{{{epub_ns}}}type", "") or nav.get("epub:type", "")
        if nav_type in epub_type:
            return True
    return False


def _nav_doc_hrefs(context: ProfileContext) -> list[Path]:
    manifest_by_id = context.opf.manifest_by_id
    seen: set[Path] = set()
    paths: list[Path] = []
    for item in context.opf.manifest:
        if "nav" not in item.properties or not item.href:
            continue
        path = context.opf_dir / item.href
        if path in seen:
            continue
        seen.add(path)
        paths.append(path)
    for item in context.opf.spine:
        manifest_item = manifest_by_id.get(item.idref)
        if manifest_item is None or not manifest_item.href:
            continue
        if "nav" not in manifest_item.properties:
            continue
        path = context.opf_dir / manifest_item.href
        if path in seen:
            continue
        seen.add(path)
        paths.append(path)
    return paths


def _validate_dc_type(context: ProfileContext) -> list[ResultMessage]:
    if is_profile_active(context, "edupub"):
        return []
    return [
        build_message(
            "RSC-005",
            path=str(context.opf_path),
            message="The dc:type identifier 'edupub' is required.",
        )
    ]


def _validate_toc_and_pagelist(context: ProfileContext) -> list[ResultMessage]:
    errors: list[ResultMessage] = []
    nav_docs = _nav_doc_hrefs(context)
    has_toc = any(_find_nav_with_type(p, "toc") for p in nav_docs)
    has_page_list = any(_find_nav_with_type(p, "page-list") for p in nav_docs)
    if not has_toc:
        errors.append(
            build_message(
                "RSC-005",
                path=str(context.opf_path),
                message="EDUPUB TOC missing",
            )
        )
    if not has_page_list:
        errors.append(
            build_message(
                "NAV-003",
                path=str(context.opf_path),
                message="EDUPUB page list missing",
            )
        )
    return errors


def _validate_accessibility_features(context: ProfileContext) -> list[ResultMessage]:
    if context.opf.xml_doc is None or context.opf.xml_doc.root is None:
        return []
    opf_ns = "http://www.idpf.org/2007/opf"
    for meta in context.opf.xml_doc.root.iter(f"{{{opf_ns}}}meta"):
        prop = meta.get("property", "")
        if prop == "schema:accessibilityFeature":
            return []
    return [
        build_message(
            "RSC-005",
            path=str(context.opf_path),
            message=("At least one schema:accessibilityFeature declaration is required for EDUPUB publications."),
        )
    ]


def _validate_content_documents(context: ProfileContext) -> list[ResultMessage]:
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

    for item in context.opf.manifest:
        if not item.href or item.media_type != "application/xhtml+xml":
            continue
        if "nav" in item.properties:
            continue
        path = context.opf_dir / item.href
        if not path.exists():
            continue
        xml_doc = load_xml(path)
        if xml_doc.errors or xml_doc.root is None:
            continue
        for body in xml_doc.root.iter(f"{{{xhtml_ns}}}body"):
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
                            "Body element used as section must contain a heading element (h1-h6 or role='heading')."
                        ),
                    )
                )
    return errors


def run(context: ProfileContext) -> list[ResultMessage]:
    is_edupub = context.requested_profile == "edupub" or is_profile_active(context, "edupub")
    if not is_edupub:
        return []
    errors: list[ResultMessage] = []
    errors.extend(_validate_dc_type(context))
    errors.extend(_validate_toc_and_pagelist(context))
    errors.extend(_validate_accessibility_features(context))
    errors.extend(_validate_content_documents(context))
    return errors
