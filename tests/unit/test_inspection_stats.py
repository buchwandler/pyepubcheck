from __future__ import annotations

from pathlib import Path

from pyepubcheck.inspect import inspect_path


def _cli_fixture(fixtures, name: str) -> Path:
    return fixtures.fixture_path("/cli/files", name)


def test_stats_count_linear_spine_text_only(fixtures) -> None:
    report = inspect_path(_cli_fixture(fixtures, "valid.epub"))

    assert report.stats is not None
    assert report.stats.content_documents == 2
    assert report.stats.linear_content_documents == 1
    assert report.stats.words == 4
    assert report.stats.estimated_pages is None
    assert report.stats.per_document[0]["path"] == "OPS/content_001.xhtml"


def test_stats_only_estimate_pages_when_requested(tmp_path: Path) -> None:
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
    <dc:title>Stats Test</dc:title>
    <dc:language>en</dc:language>
  </metadata>
  <manifest>
    <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
    <item id="chapter2" href="chapter2.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine>
    <itemref idref="chapter1"/>
    <itemref idref="chapter2" linear="no"/>
  </spine>
</package>
""",
        encoding="utf-8",
    )
    (root / "OPS" / "chapter1.xhtml").write_text(
        "<html xmlns='http://www.w3.org/1999/xhtml'><body><p>one two three four five</p><nav>skip this nav text</nav></body></html>",
        encoding="utf-8",
    )
    (root / "OPS" / "chapter2.xhtml").write_text(
        "<html xmlns='http://www.w3.org/1999/xhtml'><body><p>ignored non linear text</p></body></html>",
        encoding="utf-8",
    )

    report = inspect_path(root, estimate_pages=True, words_per_page=2)

    assert report.stats is not None
    assert report.stats.words == 5
    assert report.stats.estimated_pages == 3
    assert report.stats.linear_content_documents == 1
