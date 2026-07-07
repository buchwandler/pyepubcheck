"""CSV inspection renderers."""

from __future__ import annotations

import csv
import io

from pyepubcheck.inspect.models import ImageAsset, ManifestAsset


def render_images_csv(images: list[ImageAsset]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["path", "format", "width", "height", "size_bytes", "media_type", "referenced_by", "properties"])
    for image in images:
        writer.writerow(
            [
                image.path,
                image.format,
                image.width,
                image.height,
                image.size_bytes,
                image.media_type,
                ";".join(image.referenced_by),
                ";".join(image.properties),
            ]
        )
    return buffer.getvalue()


def render_manifest_csv(manifest: list[ManifestAsset]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "id",
            "href",
            "path",
            "media_type",
            "exists",
            "size_bytes",
            "compressed_size_bytes",
            "compression_method",
            "is_spine_item",
            "spine_index",
            "linear",
        ]
    )
    for asset in manifest:
        writer.writerow(
            [
                asset.id,
                asset.href,
                asset.path,
                asset.media_type,
                asset.exists,
                asset.size_bytes,
                asset.compressed_size_bytes,
                asset.compression_method,
                asset.is_spine_item,
                asset.spine_index,
                asset.linear,
            ]
        )
    return buffer.getvalue()
