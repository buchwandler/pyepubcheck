"""JSON inspection rendering."""

from __future__ import annotations

import json

from pyepubcheck.inspect.models import InspectionReport


def inspection_report_to_data(report: InspectionReport) -> dict[str, object]:
    return {
        "inputPath": report.input_path,
        "container": {
            "kind": report.container.kind,
            "mimetype": report.container.mimetype,
            "rootfiles": report.container.rootfiles,
            "totalEntries": report.container.total_entries,
            "totalBytes": report.container.total_bytes,
        },
        "packages": [
            {
                "path": package.path,
                "version": package.version,
                "uniqueIdentifierId": package.unique_identifier_id,
                "uniqueIdentifierValue": package.unique_identifier_value,
                "primaryLanguage": package.primary_language,
                "title": package.title,
                "renditionLayout": package.rendition_layout,
                "spineCount": package.spine_count,
                "linearSpineCount": package.linear_spine_count,
            }
            for package in report.packages
        ],
        "metadata": [
            {
                "packagePath": entry.package_path,
                "namespace": entry.namespace,
                "name": entry.name,
                "value": entry.value,
                "attributes": entry.attributes,
            }
            for entry in report.metadata
        ],
        "manifest": [
            {
                "packagePath": asset.package_path,
                "id": asset.id,
                "href": asset.href,
                "path": asset.path,
                "mediaType": asset.media_type,
                "properties": asset.properties,
                "fallback": asset.fallback,
                "mediaOverlay": asset.media_overlay,
                "exists": asset.exists,
                "sizeBytes": asset.size_bytes,
                "compressedSizeBytes": asset.compressed_size_bytes,
                "compressionMethod": asset.compression_method,
                "isSpineItem": asset.is_spine_item,
                "spineIndex": asset.spine_index,
                "linear": asset.linear,
            }
            for asset in report.manifest
        ],
        "images": [
            {
                "packagePath": image.package_path,
                "id": image.id,
                "href": image.href,
                "path": image.path,
                "mediaType": image.media_type,
                "format": image.format,
                "width": image.width,
                "height": image.height,
                "sizeBytes": image.size_bytes,
                "compressedSizeBytes": image.compressed_size_bytes,
                "properties": image.properties,
                "referencedBy": image.referenced_by,
                "exists": image.exists,
                "parseError": image.parse_error,
            }
            for image in report.images
        ],
        "navigation": None
        if report.navigation is None
        else {
            "tocEntries": [
                {
                    "label": entry.label,
                    "href": entry.href,
                    "depth": entry.depth,
                    "source": entry.source,
                    "targetExists": entry.target_exists,
                }
                for entry in report.navigation.toc_entries
            ],
            "pageListEntries": [
                {
                    "label": entry.label,
                    "href": entry.href,
                    "depth": entry.depth,
                    "source": entry.source,
                    "targetExists": entry.target_exists,
                }
                for entry in report.navigation.page_list_entries
            ],
            "landmarkEntries": [
                {
                    "label": entry.label,
                    "href": entry.href,
                    "depth": entry.depth,
                    "source": entry.source,
                    "targetExists": entry.target_exists,
                }
                for entry in report.navigation.landmark_entries
            ],
            "navDocuments": report.navigation.nav_documents,
            "ncxDocuments": report.navigation.ncx_documents,
        },
        "stats": None
        if report.stats is None
        else {
            "contentDocuments": report.stats.content_documents,
            "linearContentDocuments": report.stats.linear_content_documents,
            "words": report.stats.words,
            "characters": report.stats.characters,
            "estimatedPages": report.stats.estimated_pages,
            "perDocument": report.stats.per_document,
        },
        "warnings": report.warnings,
    }


def render_inspection_json(report: InspectionReport) -> str:
    data = inspection_report_to_data(report)
    return json.dumps(data, indent=2, sort_keys=True) + "\n"
