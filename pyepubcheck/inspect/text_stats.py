"""Text statistics for inspection."""

from __future__ import annotations

import math
import re

from pyepubcheck.inspect.models import TextStats
from pyepubcheck.xml_parser import load_xml_bytes

WORD_RE = re.compile(r"\b\w+(?:['’\-]\w+)*\b", re.UNICODE)
_SKIP_TAGS = {"script", "style", "svg", "math", "nav", "head"}


def inspect_text_stats(
    source,
    manifest_assets,
    warnings: list[str],
    *,
    estimate_pages: bool = False,
    words_per_page: int = 250,
) -> TextStats:
    """Estimate publication text statistics from spine XHTML documents."""

    xhtml_assets = [asset for asset in manifest_assets if asset.media_type == "application/xhtml+xml"]
    linear_assets = [asset for asset in xhtml_assets if asset.is_spine_item and asset.linear is not False]

    total_words = 0
    total_characters = 0
    per_document: list[dict[str, object]] = []
    for asset in linear_assets:
        if not asset.exists:
            continue
        try:
            doc = load_xml_bytes(source.read_bytes(asset.path), path=asset.path)
        except (FileNotFoundError, KeyError, ValueError):
            continue
        if doc.errors:
            warnings.append(doc.errors[0].message)
            continue
        text = _collect_visible_text(doc.root)
        normalized = " ".join(text.split())
        words = len(WORD_RE.findall(normalized))
        characters = len(normalized)
        total_words += words
        total_characters += characters
        per_document.append({"path": asset.path, "words": words, "characters": characters})

    estimated_pages = None
    if estimate_pages and words_per_page > 0:
        estimated_pages = math.ceil(total_words / words_per_page) if total_words else 0

    return TextStats(
        content_documents=len(xhtml_assets),
        linear_content_documents=len(linear_assets),
        words=total_words,
        characters=total_characters,
        estimated_pages=estimated_pages,
        per_document=per_document,
    )


def _collect_visible_text(element) -> str:
    if not isinstance(element.tag, str):
        return ""
    tag = element.tag.split("}", 1)[-1]
    if tag in _SKIP_TAGS:
        return ""

    parts: list[str] = []
    if element.text:
        parts.append(element.text)
    for child in element:
        parts.append(_collect_visible_text(child))
        if child.tail:
            parts.append(child.tail)
    return " ".join(part for part in parts if part)
