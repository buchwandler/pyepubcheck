"""JSON report rendering."""

from __future__ import annotations

import json

from pyepubcheck.result import ValidationReport


def render_json_report(report: ValidationReport) -> str:
    data = {
        "inputPath": str(report.input_path) if report.input_path is not None else "",
        "version": report.version,
        "profile": report.profile,
        "title": report.metadata.title,
        "messages": [
            {
                "id": message.id,
                "severity": message.severity.value,
                "message": message.message,
                "path": message.path,
                "line": message.line,
                "column": message.column,
            }
            for message in report.messages
        ],
        "items": [
            {
                "path": item.path,
                "mediaType": item.media_type,
                "referencedItems": list(item.referenced_items),
                "isSpineItem": item.is_spine_item,
                "isFixedFormat": item.is_fixed_format,
            }
            for item in report.items
        ],
        "publication": {
            "title": report.metadata.title,
            "refFonts": list(report.metadata.ref_fonts),
            "embeddedFonts": list(report.metadata.embedded_fonts),
            "renditionLayout": report.metadata.rendition_layout,
            "renditionOrientation": report.metadata.rendition_orientation,
            "renditionSpread": report.metadata.rendition_spread,
            "hasFixedFormat": report.metadata.has_fixed_format,
        },
    }
    return json.dumps(data, indent=2, sort_keys=True) + "\n"
