"""Markdown inspection rendering."""

from __future__ import annotations

from pyepubcheck.inspect.models import InspectionReport


def render_inspection_markdown(report: InspectionReport) -> str:
    lines = [f"# Inspection report for `{report.input_path}`", ""]
    if report.packages:
        lines.extend(["## Packages", "", "| Path | Version | Title | Language |", "| --- | --- | --- | --- |"])
        for package in report.packages:
            lines.append(
                f"| `{package.path}` | {package.version} | {package.title or '-'} | {package.primary_language or '-'} |"
            )
        lines.append("")
    if report.images:
        lines.extend(["## Images", "", "| Path | Format | Dimensions | Size |", "| --- | --- | --- | --- |"])
        for image in report.images:
            dimensions = (
                f"{image.width}x{image.height}" if image.width is not None and image.height is not None else "-"
            )
            size = "-" if image.size_bytes is None else str(image.size_bytes)
            lines.append(f"| `{image.path}` | {image.format} | {dimensions} | {size} |")
        lines.append("")
    if report.manifest:
        lines.extend(["## Manifest", "", "| ID | Path | Media type | Exists |", "| --- | --- | --- | --- |"])
        for asset in report.manifest:
            lines.append(f"| `{asset.id}` | `{asset.path}` | {asset.media_type} | {'yes' if asset.exists else 'no'} |")
        lines.append("")
    if report.navigation is not None:
        lines.extend(["## Navigation", ""])
        for entry in report.navigation.toc_entries:
            lines.append(f"- TOC depth {entry.depth}: {entry.label} -> `{entry.href}`")
        for entry in report.navigation.landmark_entries:
            lines.append(f"- Landmark: {entry.label} -> `{entry.href}`")
        lines.append(f"- Page-list entries: {len(report.navigation.page_list_entries)}")
        lines.append("")
    if report.stats is not None:
        lines.extend(["## Statistics", ""])
        lines.append(f"- Linear content documents: {report.stats.linear_content_documents}")
        lines.append(f"- XHTML content documents: {report.stats.content_documents}")
        lines.append(f"- Word count: {report.stats.words} estimated")
        lines.append(f"- Character count: {report.stats.characters}")
        if report.stats.estimated_pages is not None:
            lines.append(f"- Estimated pages: {report.stats.estimated_pages}")
        lines.append("")
    if report.metadata:
        lines.extend(["## Metadata", ""])
        for entry in report.metadata:
            lines.append(f"- `{entry.package_path}` {entry.name}: {entry.value}")
        lines.append("")
    if report.warnings:
        lines.extend(["## Warnings", ""])
        for warning in report.warnings:
            lines.append(f"- {warning}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
