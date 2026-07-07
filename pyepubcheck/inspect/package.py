"""Container and package helpers for inspection."""

from __future__ import annotations

from dataclasses import dataclass

from lxml import etree

CONTAINER_NS = "urn:oasis:names:tc:opendocument:xmlns:container"


@dataclass(frozen=True)
class Rootfile:
    full_path: str
    media_type: str


def parse_container_document(xml_bytes: bytes, logical_path: str = "META-INF/container.xml") -> list[Rootfile]:
    """Parse a container.xml document and return all declared rootfiles."""

    try:
        root = etree.fromstring(xml_bytes)
    except etree.XMLSyntaxError as exc:
        raise ValueError(f"invalid container document {logical_path}: {exc}") from exc

    rootfiles: list[Rootfile] = []
    for element in root.findall(f".//{{{CONTAINER_NS}}}rootfile"):
        full_path = (element.get("full-path") or "").strip()
        if not full_path:
            continue
        rootfiles.append(Rootfile(full_path=full_path, media_type=(element.get("media-type") or "").strip()))
    return rootfiles
