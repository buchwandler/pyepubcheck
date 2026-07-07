"""Inspection domain models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ContainerInfo:
    kind: str
    mimetype: str = ""
    rootfiles: list[str] = field(default_factory=list)
    total_entries: int = 0
    total_bytes: int = 0


@dataclass
class PackageInfo:
    path: str
    version: str
    unique_identifier_id: str = ""
    unique_identifier_value: str = ""
    primary_language: str = ""
    title: str = ""
    rendition_layout: str = ""
    spine_count: int = 0
    linear_spine_count: int = 0


@dataclass
class MetadataEntry:
    package_path: str
    namespace: str
    name: str
    value: str
    attributes: dict[str, str] = field(default_factory=dict)


@dataclass
class ManifestAsset:
    package_path: str
    id: str
    href: str
    path: str
    media_type: str
    properties: list[str] = field(default_factory=list)
    fallback: str = ""
    media_overlay: str = ""
    exists: bool = False
    size_bytes: int | None = None
    compressed_size_bytes: int | None = None
    compression_method: int | None = None
    is_spine_item: bool = False
    spine_index: int | None = None
    linear: bool | None = None


@dataclass
class ImageAsset:
    package_path: str
    id: str
    href: str
    path: str
    media_type: str
    format: str
    width: int | None = None
    height: int | None = None
    size_bytes: int | None = None
    compressed_size_bytes: int | None = None
    properties: list[str] = field(default_factory=list)
    referenced_by: list[str] = field(default_factory=list)
    exists: bool = False
    parse_error: str = ""


@dataclass
class TocEntry:
    label: str
    href: str
    depth: int
    source: str
    target_exists: bool | None = None


@dataclass
class NavigationInfo:
    toc_entries: list[TocEntry] = field(default_factory=list)
    page_list_entries: list[TocEntry] = field(default_factory=list)
    landmark_entries: list[TocEntry] = field(default_factory=list)
    nav_documents: list[str] = field(default_factory=list)
    ncx_documents: list[str] = field(default_factory=list)


@dataclass
class TextStats:
    content_documents: int = 0
    linear_content_documents: int = 0
    words: int = 0
    characters: int = 0
    estimated_pages: int | None = None
    per_document: list[dict[str, object]] = field(default_factory=list)


@dataclass
class InspectionReport:
    input_path: str
    container: ContainerInfo
    packages: list[PackageInfo] = field(default_factory=list)
    metadata: list[MetadataEntry] = field(default_factory=list)
    manifest: list[ManifestAsset] = field(default_factory=list)
    images: list[ImageAsset] = field(default_factory=list)
    navigation: NavigationInfo | None = None
    stats: TextStats | None = None
    warnings: list[str] = field(default_factory=list)
