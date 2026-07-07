from __future__ import annotations

from pathlib import Path

from pyepubcheck.inspect import inspect_manifest, inspect_metadata, inspect_path


def _cli_fixture(fixtures, name: str) -> Path:
    return fixtures.fixture_path("/cli/files", name)


def test_inspect_path_reads_container_packages_metadata_and_manifest(fixtures) -> None:
    report = inspect_path(_cli_fixture(fixtures, "valid.epub"))

    assert report.container.kind == "zip"
    assert report.container.rootfiles == ["OPS/package.opf"]
    assert report.packages[0].path == "OPS/package.opf"
    assert report.packages[0].title == "Minimal EPUB 3.0"
    assert report.packages[0].unique_identifier_value == "NOID"
    assert any(entry.name == "title" and entry.value == "Minimal EPUB 3.0" for entry in report.metadata)
    assert any(asset.id == "content_001" and asset.path == "OPS/content_001.xhtml" for asset in report.manifest)
    assert all(asset.exists for asset in report.manifest)


def test_inspect_metadata_reads_expanded_publication(fixtures) -> None:
    metadata = inspect_metadata(_cli_fixture(fixtures, "20-warning-tester"))

    assert any(entry.name == "title" and entry.value == "Minimal EPUB 2.0" for entry in metadata)
    assert any(entry.name == "version" and entry.value == "2.0" for entry in metadata)


def test_inspect_manifest_marks_missing_assets(tmp_path: Path) -> None:
    root = tmp_path / "book"
    (root / "META-INF").mkdir(parents=True)
    (root / "OPS").mkdir()
    (root / "mimetype").write_text("application/epub+zip", encoding="utf-8")
    (root / "META-INF" / "container.xml").write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OPS/package.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
""",
        encoding="utf-8",
    )
    (root / "OPS" / "package.opf").write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345</dc:identifier>
    <dc:title>Test Book</dc:title>
    <dc:language>en</dc:language>
  </metadata>
  <manifest>
    <item id="present" href="chapter.xhtml" media-type="application/xhtml+xml"/>
    <item id="missing" href="missing.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine>
    <itemref idref="present"/>
  </spine>
</package>
""",
        encoding="utf-8",
    )
    (root / "OPS" / "chapter.xhtml").write_text("<html/>", encoding="utf-8")

    manifest = inspect_manifest(root)

    assert any(asset.id == "present" and asset.exists and asset.is_spine_item for asset in manifest)
    assert any(asset.id == "missing" and not asset.exists for asset in manifest)
