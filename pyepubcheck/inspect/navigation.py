"""Navigation inspection helpers."""

from __future__ import annotations

from lxml import etree

from pyepubcheck.inspect.models import NavigationInfo, TocEntry
from pyepubcheck.inspect.source import PublicationSource, resolve_relative_path
from pyepubcheck.xml_parser import EPUB_NS, load_xml_bytes


def inspect_navigation(source: PublicationSource, manifest_assets, warnings: list[str]) -> NavigationInfo:
    """Inspect EPUB navigation documents and NCX files."""

    navigation = NavigationInfo()
    for asset in manifest_assets:
        if asset.media_type == "application/xhtml+xml" and "nav" in asset.properties:
            navigation.nav_documents.append(asset.path)
            _inspect_nav_document(source, asset.path, navigation, warnings)
        elif asset.media_type == "application/x-dtbncx+xml":
            navigation.ncx_documents.append(asset.path)
            _inspect_ncx_document(source, asset.path, navigation, warnings)
    return navigation


def _inspect_nav_document(
    source: PublicationSource,
    document_path: str,
    navigation: NavigationInfo,
    warnings: list[str],
) -> None:
    try:
        doc = load_xml_bytes(source.read_bytes(document_path), path=document_path)
    except (FileNotFoundError, KeyError, ValueError):
        return
    if doc.errors:
        warnings.append(doc.errors[0].message)
        return

    for nav in doc.root.iter():
        if not isinstance(nav.tag, str) or _local_name(nav.tag) != "nav":
            continue
        nav_type = (nav.get(f"{{{EPUB_NS}}}type") or nav.get("type") or "").strip()
        if "toc" in nav_type.split():
            navigation.toc_entries.extend(_collect_nav_list_entries(nav, document_path, source, entry_source="nav"))
        elif "landmarks" in nav_type.split():
            navigation.landmark_entries.extend(
                _collect_nav_list_entries(nav, document_path, source, entry_source="landmarks")
            )
        elif "page-list" in nav_type.split():
            navigation.page_list_entries.extend(
                _collect_nav_list_entries(nav, document_path, source, entry_source="page-list")
            )


def _inspect_ncx_document(
    source: PublicationSource,
    document_path: str,
    navigation: NavigationInfo,
    warnings: list[str],
) -> None:
    try:
        doc = load_xml_bytes(source.read_bytes(document_path), path=document_path)
    except (FileNotFoundError, KeyError, ValueError):
        return
    if doc.errors:
        warnings.append(doc.errors[0].message)
        return

    root = doc.root
    nav_map = _first_child(root, "navMap")
    if nav_map is not None:
        for nav_point in _children(nav_map, "navPoint"):
            navigation.toc_entries.extend(
                _collect_ncx_points(nav_point, document_path, source, depth=1, entry_source="ncx")
            )

    page_list = _first_child(root, "pageList")
    if page_list is not None:
        for page_target in _children(page_list, "pageTarget"):
            navigation.page_list_entries.extend(
                _collect_ncx_points(page_target, document_path, source, depth=1, entry_source="page-list")
            )


def _collect_nav_list_entries(
    nav: etree._Element,
    document_path: str,
    source: PublicationSource,
    *,
    entry_source: str,
) -> list[TocEntry]:
    ordered_lists = [
        child for child in nav.iterchildren() if isinstance(child.tag, str) and _local_name(child.tag) == "ol"
    ]
    entries: list[TocEntry] = []
    for ordered_list in ordered_lists:
        entries.extend(
            _collect_html_list_entries(
                ordered_list,
                document_path,
                source,
                depth=1,
                entry_source=entry_source,
            )
        )
    return entries


def _collect_html_list_entries(
    ordered_list: etree._Element,
    document_path: str,
    source: PublicationSource,
    *,
    depth: int,
    entry_source: str,
) -> list[TocEntry]:
    entries: list[TocEntry] = []
    for item in ordered_list.iterchildren():
        if not isinstance(item.tag, str) or _local_name(item.tag) != "li":
            continue
        anchor = _first_descendant(item, "a")
        label = "".join(anchor.itertext()).strip() if anchor is not None else "".join(item.itertext()).strip()
        href = (anchor.get("href") or "").strip() if anchor is not None else ""
        entries.append(
            TocEntry(
                label=label,
                href=href,
                depth=depth,
                source=entry_source,
                target_exists=_target_exists(source, document_path, href),
            )
        )
        for child in item.iterchildren():
            if isinstance(child.tag, str) and _local_name(child.tag) == "ol":
                entries.extend(
                    _collect_html_list_entries(
                        child,
                        document_path,
                        source,
                        depth=depth + 1,
                        entry_source=entry_source,
                    )
                )
    return entries


def _collect_ncx_points(
    point: etree._Element,
    document_path: str,
    source: PublicationSource,
    *,
    depth: int,
    entry_source: str,
) -> list[TocEntry]:
    label = ""
    nav_label = _first_child(point, "navLabel")
    if nav_label is not None:
        text = _first_child(nav_label, "text")
        if text is not None and text.text:
            label = text.text.strip()
    content = _first_child(point, "content")
    href = (content.get("src") or "").strip() if content is not None else ""
    entries = [
        TocEntry(
            label=label,
            href=href,
            depth=depth,
            source=entry_source,
            target_exists=_target_exists(source, document_path, href),
        )
    ]
    for child in point.iterchildren():
        if isinstance(child.tag, str) and _local_name(child.tag) in {"navPoint", "pageTarget"}:
            entries.extend(
                _collect_ncx_points(
                    child,
                    document_path,
                    source,
                    depth=depth + 1,
                    entry_source=entry_source,
                )
            )
    return entries


def _target_exists(source: PublicationSource, document_path: str, href: str) -> bool | None:
    if not href:
        return None
    try:
        return source.exists(resolve_relative_path(document_path, href))
    except ValueError:
        return None


def _local_name(tag: str) -> str:
    return tag.split("}", 1)[-1]


def _first_descendant(element: etree._Element, name: str) -> etree._Element | None:
    for child in element.iterdescendants():
        if isinstance(child.tag, str) and _local_name(child.tag) == name:
            return child
    return None


def _first_child(element: etree._Element, name: str) -> etree._Element | None:
    for child in element.iterchildren():
        if isinstance(child.tag, str) and _local_name(child.tag) == name:
            return child
    return None


def _children(element: etree._Element, name: str) -> list[etree._Element]:
    return [child for child in element.iterchildren() if isinstance(child.tag, str) and _local_name(child.tag) == name]
