from __future__ import annotations

from pathlib import Path

from pyepubcheck.inspect import inspect_path


def _cli_fixture(fixtures, name: str) -> Path:
    return fixtures.fixture_path("/cli/files", name)


def test_navigation_uses_epub3_nav_document(fixtures) -> None:
    report = inspect_path(_cli_fixture(fixtures, "valid.epub"))

    assert report.navigation is not None
    assert report.navigation.nav_documents == ["OPS/nav.xhtml"]
    assert len(report.navigation.toc_entries) == 1
    assert report.navigation.toc_entries[0].href == "content_001.xhtml"
    assert report.navigation.toc_entries[0].target_exists is True
    assert len(report.navigation.landmark_entries) == 1
    assert report.navigation.page_list_entries == []


def test_navigation_collects_page_list_from_ncx(tmp_path: Path) -> None:
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
<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345</dc:identifier>
    <dc:title>NCX Test</dc:title>
    <dc:language>en</dc:language>
  </metadata>
  <manifest>
    <item id="chapter" href="chapter.xhtml" media-type="application/xhtml+xml"/>
    <item id="toc" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
  </manifest>
  <spine toc="toc">
    <itemref idref="chapter"/>
  </spine>
</package>
""",
        encoding="utf-8",
    )
    (root / "OPS" / "toc.ncx").write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <navMap>
    <navPoint id="navPoint-1">
      <navLabel><text>Chapter 1</text></navLabel>
      <content src="chapter.xhtml"/>
    </navPoint>
  </navMap>
  <pageList>
    <pageTarget id="page-1" type="normal" value="1">
      <navLabel><text>1</text></navLabel>
      <content src="chapter.xhtml#p1"/>
    </pageTarget>
  </pageList>
</ncx>
""",
        encoding="utf-8",
    )
    (root / "OPS" / "chapter.xhtml").write_text("<html/>", encoding="utf-8")

    report = inspect_path(root)

    assert report.navigation is not None
    assert report.navigation.ncx_documents == ["OPS/toc.ncx"]
    assert len(report.navigation.toc_entries) == 1
    assert len(report.navigation.page_list_entries) == 1
    assert report.navigation.page_list_entries[0].label == "1"
