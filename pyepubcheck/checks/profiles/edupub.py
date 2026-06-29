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


def run(context: ProfileContext) -> list[ResultMessage]:
    is_edupub = context.requested_profile == "edupub" or is_profile_active(
        context, "edupub"
    )
    if not is_edupub:
        return []
    errors: list[ResultMessage] = []
    errors.extend(_validate_dc_type(context))
    errors.extend(_validate_toc_and_pagelist(context))
    return errors
