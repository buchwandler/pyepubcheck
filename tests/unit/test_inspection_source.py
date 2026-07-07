from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from pyepubcheck.inspect.package import parse_container_document
from pyepubcheck.inspect.source import (
    DirectoryPublicationSource,
    ZipPublicationSource,
    open_publication_source,
    resolve_relative_path,
    safe_relative_path,
)


def test_zip_publication_source_lists_entries_and_reads_bytes(tmp_path: Path) -> None:
    archive_path = tmp_path / "book.epub"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        archive.writestr("OPS/package.opf", "<package/>")
        archive.writestr("META-INF/container.xml", "<container/>")

    source = ZipPublicationSource(archive_path)

    entries = {entry.path: entry for entry in source.entries()}
    assert set(entries) == {"mimetype", "OPS/package.opf", "META-INF/container.xml"}
    assert entries["mimetype"].size_bytes == len(b"application/epub+zip")
    assert source.exists("OPS/package.opf") is True
    assert source.read_bytes("OPS/package.opf") == b"<package/>"


def test_directory_publication_source_lists_entries_and_reads_text(tmp_path: Path) -> None:
    root = tmp_path / "book"
    (root / "OPS").mkdir(parents=True)
    (root / "OPS" / "package.opf").write_text("<package/>", encoding="utf-8")
    (root / "mimetype").write_text("application/epub+zip", encoding="utf-8")

    source = DirectoryPublicationSource(root)

    entries = {entry.path: entry for entry in source.entries()}
    assert set(entries) == {"OPS/package.opf", "mimetype"}
    assert source.exists("OPS/package.opf") is True
    assert source.read_text("OPS/package.opf") == "<package/>"


def test_open_publication_source_detects_zip_and_directory(tmp_path: Path) -> None:
    directory = tmp_path / "expanded"
    directory.mkdir()
    archive = tmp_path / "book.epub"
    archive.write_bytes(b"PK\x03\x04")

    assert open_publication_source(directory).kind == "directory"
    assert open_publication_source(archive).kind == "zip"


def test_safe_relative_path_rejects_traversal() -> None:
    assert safe_relative_path("OPS/../OPS/package.opf") == "OPS/package.opf"
    with pytest.raises(ValueError):
        safe_relative_path("../OPS/package.opf")
    with pytest.raises(ValueError):
        safe_relative_path("/OPS/package.opf")


def test_resolve_relative_path_normalizes_against_base_path() -> None:
    assert resolve_relative_path("OPS/text/chapter.xhtml", "../images/cover.png") == "OPS/images/cover.png"
    assert resolve_relative_path("OPS/text/chapter.xhtml", "figure.png#frag") == "OPS/text/figure.png"


def test_parse_container_document_returns_all_rootfiles() -> None:
    rootfiles = parse_container_document(
        b"""<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OPS/package.opf" media-type="application/oebps-package+xml"/>
    <rootfile full-path="ALT/package.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""
    )

    assert [rootfile.full_path for rootfile in rootfiles] == ["OPS/package.opf", "ALT/package.opf"]
