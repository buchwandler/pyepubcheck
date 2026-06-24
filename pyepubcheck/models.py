"""Domain models shared by reports and checks."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PublicationItem:
    path: str
    media_type: str = ""
    referenced_items: tuple[str, ...] = ()
    is_spine_item: bool = False
    is_fixed_format: bool = False


@dataclass
class PublicationMetadata:
    title: str = ""
    ref_fonts: tuple[str, ...] = ()
    embedded_fonts: tuple[str, ...] = ()
    rendition_layout: str | None = None
    rendition_orientation: str | None = None
    rendition_spread: str | None = None
    has_fixed_format: bool = False
    extra: dict[str, object] = field(default_factory=dict)
