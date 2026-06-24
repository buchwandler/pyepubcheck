"""XMP report rendering."""

from __future__ import annotations

from pyepubcheck.result import ValidationReport


def render_xmp_report(report: ValidationReport) -> str:
    del report
    return "<xmpmeta />\n"
