"""Public inspection API."""

from __future__ import annotations

from pathlib import Path

from pyepubcheck.inspect.images import inspect_image_assets
from pyepubcheck.inspect.metadata import build_package_info, extract_metadata_entries
from pyepubcheck.inspect.models import ContainerInfo, ImageAsset, InspectionReport, ManifestAsset, MetadataEntry
from pyepubcheck.inspect.navigation import inspect_navigation
from pyepubcheck.inspect.package import Rootfile, parse_container_document
from pyepubcheck.inspect.source import PublicationSource, SourceEntry, open_publication_source, resolve_relative_path
from pyepubcheck.inspect.text_stats import inspect_text_stats
from pyepubcheck.io.urls import is_data_url, is_remote_url
from pyepubcheck.opf_parser import parse_opf_document


def inspect_path(path: str | Path, *, estimate_pages: bool = False, words_per_page: int = 250) -> InspectionReport:
    """Inspect a packaged EPUB or expanded EPUB directory."""

    input_path = Path(path)
    source = open_publication_source(input_path)
    entries = source.entries()
    entry_by_path = {entry.path: entry for entry in entries}
    warnings: list[str] = []

    rootfiles = _resolve_rootfiles(source, warnings)
    container = ContainerInfo(
        kind=source.kind,
        mimetype=_read_optional_text(source, "mimetype"),
        rootfiles=[rootfile.full_path for rootfile in rootfiles],
        total_entries=len(entries),
        total_bytes=sum(entry.size_bytes for entry in entries),
    )

    report = InspectionReport(input_path=str(input_path), container=container, warnings=warnings)
    all_navigation = None
    all_manifest_assets: list[ManifestAsset] = []

    for rootfile in rootfiles:
        try:
            opf = parse_opf_document(source.read_bytes(rootfile.full_path), rootfile.full_path)
        except (FileNotFoundError, KeyError, ValueError) as exc:
            report.warnings.append(str(exc))
            continue
        if opf.errors:
            report.warnings.extend(message.message for message in opf.errors)
            continue

        report.packages.append(build_package_info(rootfile.full_path, opf))
        report.metadata.extend(extract_metadata_entries(rootfile.full_path, opf))
        package_manifest = _build_manifest_assets(source, rootfile.full_path, opf, entry_by_path)
        report.manifest.extend(package_manifest)
        all_manifest_assets.extend(package_manifest)
        report.images.extend(inspect_image_assets(source, rootfile.full_path, package_manifest, report.warnings))
        package_navigation = inspect_navigation(source, package_manifest, report.warnings)
        if all_navigation is None:
            all_navigation = package_navigation
        else:
            all_navigation.toc_entries.extend(package_navigation.toc_entries)
            all_navigation.page_list_entries.extend(package_navigation.page_list_entries)
            all_navigation.landmark_entries.extend(package_navigation.landmark_entries)
            all_navigation.nav_documents.extend(package_navigation.nav_documents)
            all_navigation.ncx_documents.extend(package_navigation.ncx_documents)

    report.navigation = all_navigation
    report.stats = inspect_text_stats(
        source,
        all_manifest_assets,
        report.warnings,
        estimate_pages=estimate_pages,
        words_per_page=words_per_page,
    )
    return report


def inspect_metadata(path: str | Path) -> list[MetadataEntry]:
    """Return extracted package metadata entries."""

    return inspect_path(path).metadata


def inspect_manifest(path: str | Path) -> list[ManifestAsset]:
    """Return manifest asset records."""

    return inspect_path(path).manifest


def inspect_images(path: str | Path) -> list[ImageAsset]:
    """Return image asset records."""

    return inspect_path(path).images


def _resolve_rootfiles(source: PublicationSource, warnings: list[str]) -> list[Rootfile]:
    if source.exists("META-INF/container.xml"):
        try:
            rootfiles = parse_container_document(source.read_bytes("META-INF/container.xml"))
        except ValueError as exc:
            warnings.append(str(exc))
        else:
            if rootfiles:
                return rootfiles
            warnings.append("container document did not declare any rootfiles")
    fallback_rootfiles = [
        Rootfile(full_path=entry.path, media_type="application/oebps-package+xml")
        for entry in source.entries()
        if entry.path.lower().endswith(".opf")
    ]
    return fallback_rootfiles


def _read_optional_text(source: PublicationSource, path: str) -> str:
    try:
        return source.read_text(path).strip()
    except (KeyError, FileNotFoundError, ValueError):
        return ""


def _build_manifest_assets(
    source: PublicationSource,
    package_path: str,
    opf,
    entry_by_path: dict[str, SourceEntry],
) -> list[ManifestAsset]:
    manifest_assets: list[ManifestAsset] = []
    spine_by_idref = {item.idref: (index, item) for index, item in enumerate(opf.spine)}

    for item in opf.manifest:
        resolved_path = item.href
        exists = False
        size_bytes = None
        compressed_size_bytes = None
        compression_method = None

        if not is_remote_url(item.href) and not is_data_url(item.href):
            resolved_path = resolve_relative_path(package_path, item.href)
            exists = source.exists(resolved_path)
            entry = entry_by_path.get(resolved_path)
            if entry is not None:
                size_bytes = entry.size_bytes
                compressed_size_bytes = entry.compressed_size_bytes
                compression_method = entry.compress_type

        spine_position, spine_item = spine_by_idref.get(item.id, (None, None))
        manifest_assets.append(
            ManifestAsset(
                package_path=package_path,
                id=item.id,
                href=item.href,
                path=resolved_path,
                media_type=item.media_type,
                properties=list(item.properties),
                fallback=item.fallback,
                media_overlay=item.media_overlay,
                exists=exists,
                size_bytes=size_bytes,
                compressed_size_bytes=compressed_size_bytes,
                compression_method=compression_method,
                is_spine_item=spine_item is not None,
                spine_index=spine_position,
                linear=spine_item.linear if spine_item is not None else None,
            )
        )
    return manifest_assets
