"""Image inspection helpers."""

from __future__ import annotations

import re
import struct
from dataclasses import dataclass, field

import tinycss2

from pyepubcheck.inspect.models import ImageAsset, ManifestAsset
from pyepubcheck.inspect.source import PublicationSource, resolve_relative_path
from pyepubcheck.io.urls import is_data_url, is_remote_url
from pyepubcheck.xml_parser import load_xml_bytes

IMAGE_MEDIA_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/svg+xml",
    "image/webp",
    "image/avif",
}

_JPEG_SOF_MARKERS = {
    0xC0,
    0xC1,
    0xC2,
    0xC3,
    0xC5,
    0xC6,
    0xC7,
    0xC9,
    0xCA,
    0xCB,
    0xCD,
    0xCE,
    0xCF,
}
_CSS_URL_RE = re.compile(r"url\((?P<value>[^)]+)\)")


@dataclass
class ImageProbeResult:
    format: str
    width: int | None
    height: int | None
    extra: dict[str, str] = field(default_factory=dict)
    error: str = ""


def inspect_image_assets(
    source: PublicationSource,
    package_path: str,
    manifest_assets: list[ManifestAsset],
    warnings: list[str],
) -> list[ImageAsset]:
    """Build image asset records from manifest assets."""

    image_assets: list[ImageAsset] = []
    image_paths = {asset.path for asset in manifest_assets if asset.media_type in IMAGE_MEDIA_TYPES}
    referenced_by = _build_references_map(source, manifest_assets, image_paths, warnings)

    for asset in manifest_assets:
        if asset.media_type not in IMAGE_MEDIA_TYPES:
            continue

        probe = ImageProbeResult(format=_format_from_media_type(asset.media_type), width=None, height=None)
        if asset.exists:
            try:
                probe = probe_image_bytes(source.read_bytes(asset.path), media_type=asset.media_type)
            except (FileNotFoundError, KeyError, ValueError) as exc:
                probe = ImageProbeResult(
                    format=_format_from_media_type(asset.media_type),
                    width=None,
                    height=None,
                    error=str(exc),
                )

        image_assets.append(
            ImageAsset(
                package_path=package_path,
                id=asset.id,
                href=asset.href,
                path=asset.path,
                media_type=asset.media_type,
                format=probe.format,
                width=probe.width,
                height=probe.height,
                size_bytes=asset.size_bytes,
                compressed_size_bytes=asset.compressed_size_bytes,
                properties=list(asset.properties),
                referenced_by=sorted(referenced_by.get(asset.path, set())),
                exists=asset.exists,
                parse_error=probe.error,
            )
        )
    return image_assets


def probe_image_bytes(data: bytes, media_type: str = "") -> ImageProbeResult:
    """Detect image format and dimensions from bytes."""

    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        width, height = struct.unpack(">II", data[16:24])
        return ImageProbeResult(format="PNG", width=width, height=height)

    if data.startswith((b"GIF87a", b"GIF89a")) and len(data) >= 10:
        width, height = struct.unpack("<HH", data[6:10])
        return ImageProbeResult(format="GIF", width=width, height=height)

    if data.startswith(b"\xff\xd8"):
        return _probe_jpeg(data)

    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return _probe_webp(data)

    if b"<svg" in data[:256].lower():
        return _probe_svg(data)

    if len(data) >= 12 and data[4:12] in {b"ftypavif", b"ftypavis"}:
        return ImageProbeResult(format="AVIF", width=None, height=None)

    fallback = _format_from_media_type(media_type)
    return ImageProbeResult(format=fallback, width=None, height=None, error="unsupported or unrecognized image data")


def _probe_jpeg(data: bytes) -> ImageProbeResult:
    index = 2
    size = len(data)
    while index + 1 < size:
        if data[index] != 0xFF:
            index += 1
            continue
        while index < size and data[index] == 0xFF:
            index += 1
        if index >= size:
            break
        marker = data[index]
        index += 1
        if marker in {0xD8, 0xD9}:
            continue
        if marker == 0xDA:
            break
        if index + 2 > size:
            break
        segment_length = struct.unpack(">H", data[index : index + 2])[0]
        if segment_length < 2 or index + segment_length > size:
            break
        if marker in _JPEG_SOF_MARKERS and segment_length >= 7:
            precision = data[index + 2]
            height, width = struct.unpack(">HH", data[index + 3 : index + 7])
            if precision:
                return ImageProbeResult(format="JPEG", width=width, height=height)
        index += segment_length
    return ImageProbeResult(format="JPEG", width=None, height=None, error="could not locate JPEG dimensions")


def _probe_webp(data: bytes) -> ImageProbeResult:
    chunk = data[12:16]
    if chunk == b"VP8X" and len(data) >= 30:
        width = 1 + int.from_bytes(data[24:27], "little")
        height = 1 + int.from_bytes(data[27:30], "little")
        return ImageProbeResult(format="WEBP", width=width, height=height)
    if chunk == b"VP8L" and len(data) >= 25:
        bits = int.from_bytes(data[21:25], "little")
        width = (bits & 0x3FFF) + 1
        height = ((bits >> 14) & 0x3FFF) + 1
        return ImageProbeResult(format="WEBP", width=width, height=height)
    if chunk == b"VP8 " and len(data) >= 30:
        start = data.find(b"\x9d\x01\x2a", 20)
        if start != -1 and start + 7 <= len(data):
            width, height = struct.unpack("<HH", data[start + 3 : start + 7])
            return ImageProbeResult(format="WEBP", width=width & 0x3FFF, height=height & 0x3FFF)
    return ImageProbeResult(format="WEBP", width=None, height=None, error="could not locate WebP dimensions")


def _probe_svg(data: bytes) -> ImageProbeResult:
    doc = load_xml_bytes(data, path="<svg>")
    if doc.errors:
        return ImageProbeResult(format="SVG", width=None, height=None, error=doc.errors[0].message)
    width = _parse_svg_length(doc.root.get("width"))
    height = _parse_svg_length(doc.root.get("height"))
    extra: dict[str, str] = {}
    view_box = (doc.root.get("viewBox") or "").strip()
    if view_box:
        extra["viewBox"] = view_box
    return ImageProbeResult(format="SVG", width=width, height=height, extra=extra)


def _parse_svg_length(value: str | None) -> int | None:
    if not value:
        return None
    cleaned = value.strip()
    if cleaned.endswith("px"):
        cleaned = cleaned[:-2]
    if cleaned.isdigit():
        return int(cleaned)
    return None


def _build_references_map(
    source: PublicationSource,
    manifest_assets: list[ManifestAsset],
    image_paths: set[str],
    warnings: list[str],
) -> dict[str, set[str]]:
    references: dict[str, set[str]] = {path: set() for path in image_paths}
    for asset in manifest_assets:
        if asset.media_type == "application/xhtml+xml":
            _record_local_references(
                asset.path,
                _extract_xml_image_references(source, asset.path, warnings, include_html=True),
                image_paths,
                references,
            )
        elif asset.media_type == "image/svg+xml":
            _record_local_references(
                asset.path,
                _extract_xml_image_references(source, asset.path, warnings, include_html=False),
                image_paths,
                references,
            )
        elif asset.media_type == "text/css":
            _record_local_references(
                asset.path,
                _extract_css_image_references(source, asset.path),
                image_paths,
                references,
            )
    return references


def _extract_xml_image_references(
    source: PublicationSource,
    document_path: str,
    warnings: list[str],
    *,
    include_html: bool,
) -> set[str]:
    try:
        data = source.read_bytes(document_path)
    except (FileNotFoundError, KeyError, ValueError):
        return set()

    doc = load_xml_bytes(data, path=document_path)
    if doc.errors:
        warnings.append(doc.errors[0].message)
        return set()

    references: set[str] = set()
    for element in doc.root.iter():
        if not isinstance(element.tag, str):
            continue
        tag = element.tag.split("}", 1)[-1]
        attrs = element.attrib

        if include_html and tag == "img" and "src" in attrs:
            references.add(attrs["src"])
        if include_html and tag == "source" and "srcset" in attrs:
            references.update(_parse_srcset(attrs["srcset"]))
        if tag == "image":
            for attr_name in ("href", "{http://www.w3.org/1999/xlink}href"):
                if attr_name in attrs:
                    references.add(attrs[attr_name])
        style = attrs.get("style")
        if style:
            references.update(_extract_css_urls(style))
    return references


def _extract_css_image_references(source: PublicationSource, document_path: str) -> set[str]:
    try:
        css_text = source.read_text(document_path)
    except (FileNotFoundError, KeyError, ValueError):
        return set()
    tinycss2.parse_stylesheet(css_text, skip_comments=True, skip_whitespace=True)
    return _extract_css_urls(css_text)


def _extract_css_urls(value: str) -> set[str]:
    results: set[str] = set()
    for match in _CSS_URL_RE.finditer(value):
        candidate = match.group("value").strip().strip("'\"")
        if candidate:
            results.add(candidate)
    return results


def _parse_srcset(srcset: str) -> set[str]:
    results: set[str] = set()
    for item in srcset.split(","):
        candidate = item.strip().split()[0] if item.strip() else ""
        if candidate:
            results.add(candidate)
    return results


def _record_local_references(
    base_path: str,
    raw_references: set[str],
    image_paths: set[str],
    references: dict[str, set[str]],
) -> None:
    for reference in raw_references:
        if is_remote_url(reference) or is_data_url(reference):
            continue
        try:
            resolved = resolve_relative_path(base_path, reference)
        except ValueError:
            continue
        if resolved in image_paths:
            references.setdefault(resolved, set()).add(base_path)


def _format_from_media_type(media_type: str) -> str:
    mapping = {
        "image/jpeg": "JPEG",
        "image/png": "PNG",
        "image/gif": "GIF",
        "image/svg+xml": "SVG",
        "image/webp": "WEBP",
        "image/avif": "AVIF",
    }
    return mapping.get(media_type, "UNKNOWN")
