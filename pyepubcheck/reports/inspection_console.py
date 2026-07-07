"""Human-readable inspection renderers."""

from __future__ import annotations

from collections import Counter

from pyepubcheck.inspect.models import (
    ImageAsset,
    InspectionReport,
    ManifestAsset,
    MetadataEntry,
    NavigationInfo,
    TextStats,
)


def render_publication_summary(report: InspectionReport) -> str:
    if not report.packages:
        return ""

    package = report.packages[0]
    lines = ["Publication summary", f"  Title: {package.title or '-'}", f"  EPUB version: {package.version or '-'}"]
    lines.append(f"  Language: {package.primary_language or '-'}")
    lines.append(f"  Layout: {package.rendition_layout or 'unknown'}")
    lines.append(f"  Chapters: {package.spine_count} spine items, {package.linear_spine_count} linear")

    if report.navigation is not None:
        lines.append(f"  Pages: {len(report.navigation.page_list_entries)} page-list entries")

    if report.stats is not None:
        line = f"  Words: {report.stats.words:,} estimated"
        if report.stats.estimated_pages is not None:
            line += f"; Pages: {report.stats.estimated_pages} estimated"
        lines.append(line)

    if report.images:
        format_counts = Counter(image.format for image in report.images)
        totals = ", ".join(f"{name} {count}" for name, count in sorted(format_counts.items()))
        total_bytes = sum(image.size_bytes or 0 for image in report.images)
        lines.append(f"  Images: {len(report.images)} total; {totals}; {_format_bytes(total_bytes)}")
        largest = max(report.images, key=lambda image: image.size_bytes or 0)
        lines.append(
            "  Largest image: "
            f"{largest.path} - {largest.format}, {_format_dimensions(largest)}, {_format_bytes(largest.size_bytes)}"
        )
    return "\n".join(lines)


def render_inspection_text(report: InspectionReport) -> str:
    sections = [f"Inspection for {report.input_path}", ""]
    summary = render_publication_summary(report)
    if summary:
        sections.extend([summary, ""])
    if report.packages:
        sections.extend(["Packages"])
        for package in report.packages:
            sections.append(f"  {package.path} ({package.version})")
        sections.append("")
    if report.images:
        sections.append(render_images_text(report.input_path, report.images))
        sections.append("")
    if report.metadata:
        sections.append(render_metadata_text(report.input_path, report.metadata, report.packages))
        sections.append("")
    if report.manifest:
        sections.append(render_manifest_text(report.input_path, report.manifest))
        sections.append("")
    if report.navigation is not None:
        sections.append(render_navigation_text(report.input_path, report.navigation))
        sections.append("")
    if report.stats is not None:
        sections.append(render_stats_text(report.input_path, report.stats))
    if report.warnings:
        sections.extend(["", "Warnings", *[f"  - {warning}" for warning in report.warnings]])
    return "\n".join(sections).rstrip() + "\n"


def render_images_text(input_path: str, images: list[ImageAsset]) -> str:
    lines = [f"Images in {input_path}", ""]
    lines.append("Path | Format | Dimensions | Size | Referenced | Properties")
    lines.append("--- | --- | --- | --- | --- | ---")
    for image in images:
        lines.append(
            " | ".join(
                [
                    image.path,
                    image.format,
                    _format_dimensions(image),
                    _format_bytes(image.size_bytes),
                    "yes" if image.referenced_by else "no",
                    " ".join(image.properties) if image.properties else "-",
                ]
            )
        )
    return "\n".join(lines)


def render_metadata_text(input_path: str, metadata: list[MetadataEntry], packages) -> str:
    lines = [f"Metadata in {input_path}", ""]
    for package in packages:
        lines.append(f"Package: {package.path}")
        lines.append(f"EPUB version: {package.version}")
        if package.unique_identifier_id or package.unique_identifier_value:
            lines.append(
                f"Unique identifier: {package.unique_identifier_id or '-'} = {package.unique_identifier_value or '-'}"
            )
    for entry in metadata:
        label = f"{entry.name}"
        if entry.namespace == "package":
            label = f"package:{entry.name}"
        lines.append(f"{label}: {entry.value}")
    return "\n".join(lines)


def render_manifest_text(input_path: str, manifest: list[ManifestAsset]) -> str:
    lines = [f"Manifest in {input_path}", ""]
    lines.append("ID | Href | Path | Media type | Exists | Size")
    lines.append("--- | --- | --- | --- | --- | ---")
    for asset in manifest:
        lines.append(
            " | ".join(
                [
                    asset.id,
                    asset.href,
                    asset.path,
                    asset.media_type,
                    "yes" if asset.exists else "no",
                    _format_bytes(asset.size_bytes),
                ]
            )
        )
    return "\n".join(lines)


def render_navigation_text(input_path: str, navigation: NavigationInfo) -> str:
    lines = [f"Navigation in {input_path}", ""]
    lines.append("TOC")
    if navigation.toc_entries:
        for entry in navigation.toc_entries:
            lines.append(f"  {'  ' * (entry.depth - 1)}- {entry.label} -> {entry.href}")
    else:
        lines.append("  (none)")
    lines.append("Landmarks")
    if navigation.landmark_entries:
        for entry in navigation.landmark_entries:
            lines.append(f"  - {entry.label} -> {entry.href}")
    else:
        lines.append("  (none)")
    lines.append(f"Page list entries: {len(navigation.page_list_entries)}")
    return "\n".join(lines)


def render_stats_text(input_path: str, stats: TextStats) -> str:
    lines = [f"Statistics in {input_path}", ""]
    lines.append(f"Linear content documents: {stats.linear_content_documents}")
    lines.append(f"XHTML content documents: {stats.content_documents}")
    lines.append(f"Word count: {stats.words} estimated")
    lines.append(f"Character count: {stats.characters}")
    if stats.estimated_pages is not None:
        lines.append(f"Estimated pages: {stats.estimated_pages}")
    return "\n".join(lines)


def _format_bytes(size: int | None) -> str:
    if size is None:
        return "-"
    units = ["B", "KiB", "MiB", "GiB"]
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{size} B"


def _format_dimensions(image: ImageAsset) -> str:
    if image.width is not None and image.height is not None:
        return f"{image.width}x{image.height}"
    return "unknown"
