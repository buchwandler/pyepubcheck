from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

from tests.support import build_epub_from_directory


def _make_png(width: int, height: int) -> bytes:
    return (
        b"\x89PNG\r\n\x1a\n"
        + b"\x00\x00\x00\rIHDR"
        + struct.pack(">II", width, height)
        + b"\x08\x02\x00\x00\x00"
        + b"\x00\x00\x00\x00"
    )


def _make_jpeg(width: int, height: int) -> bytes:
    return (
        b"\xff\xd8"
        + b"\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
        + b"\xff\xc0\x00\x11\x08"
        + struct.pack(">HH", height, width)
        + b"\x03\x01\x11\x00\x02\x11\x00\x03\x11\x00"
        + b"\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\x00"
        + b"\xff\xd9"
    )


def _build_inspection_fixture(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "inspection-basic"
    (root / "META-INF").mkdir(parents=True)
    (root / "OPS" / "images").mkdir(parents=True)
    (root / "OPS" / "styles").mkdir(parents=True)

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
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="en">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="bookid">urn:uuid:test-book</dc:identifier>
    <dc:title>Inspection Fixture</dc:title>
    <dc:language>en</dc:language>
    <dc:creator>Fixture Author</dc:creator>
    <meta property="dcterms:modified">2026-07-07T10:00:00Z</meta>
    <meta property="rendition:layout">reflowable</meta>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="chapter-1" href="chapter-001.xhtml" media-type="application/xhtml+xml"/>
    <item id="chapter-2" href="chapter-002.xhtml" media-type="application/xhtml+xml"/>
    <item id="styles" href="styles/book.css" media-type="text/css"/>
    <item id="cover" href="images/cover.png" media-type="image/png" properties="cover-image"/>
    <item id="figure" href="images/figure.jpg" media-type="image/jpeg"/>
  </manifest>
  <spine>
    <itemref idref="chapter-1"/>
    <itemref idref="chapter-2"/>
  </spine>
</package>
""",
        encoding="utf-8",
    )
    (root / "OPS" / "nav.xhtml").write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
  <head><title>Navigation</title></head>
  <body>
    <nav epub:type="toc">
      <ol>
        <li><a href="chapter-001.xhtml">Chapter 1</a></li>
        <li><a href="chapter-002.xhtml">Chapter 2</a></li>
      </ol>
    </nav>
    <nav epub:type="landmarks">
      <ol>
        <li><a href="chapter-001.xhtml" epub:type="bodymatter">Start Reading</a></li>
      </ol>
    </nav>
    <nav epub:type="page-list">
      <ol>
        <li><a href="chapter-001.xhtml#p1">1</a></li>
        <li><a href="chapter-002.xhtml#p2">2</a></li>
      </ol>
    </nav>
  </body>
</html>
""",
        encoding="utf-8",
    )
    (root / "OPS" / "chapter-001.xhtml").write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
  <head><title>Chapter 1</title><link rel="stylesheet" href="styles/book.css"/></head>
  <body>
    <h1 id="p1">Chapter 1</h1>
    <p>Call me Ishmael and let the fixture words begin.</p>
    <img src="images/cover.png" alt="Cover image"/>
  </body>
</html>
""",
        encoding="utf-8",
    )
    (root / "OPS" / "chapter-002.xhtml").write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
  <head><title>Chapter 2</title></head>
  <body>
    <h1 id="p2">Chapter 2</h1>
    <p>Another short chapter with enough words for page estimates.</p>
  </body>
</html>
""",
        encoding="utf-8",
    )
    (root / "OPS" / "styles" / "book.css").write_text(
        "body { background-image: url('../images/figure.jpg'); }",
        encoding="utf-8",
    )
    (root / "OPS" / "images" / "cover.png").write_bytes(_make_png(2400, 3600))
    (root / "OPS" / "images" / "figure.jpg").write_bytes(_make_jpeg(1600, 1100))

    return root, build_epub_from_directory(root, tmp_path / "inspection-basic.epub")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_inspect_json_returns_complete_schema(run_pyepubcheck, tmp_path: Path) -> None:
    _expanded, packaged = _build_inspection_fixture(tmp_path)

    result = run_pyepubcheck("inspect", packaged, "--format", "json", transport="subprocess")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["container"]["kind"] == "zip"
    assert payload["packages"][0]["title"] == "Inspection Fixture"
    assert payload["navigation"]["pageListEntries"][0]["label"] == "1"
    assert payload["stats"]["words"] > 0
    assert len(payload["images"]) == 2
    assert "No errors or warnings detected." not in result.stdout


def test_images_command_reports_dimensions_and_references(run_pyepubcheck, tmp_path: Path) -> None:
    _expanded, packaged = _build_inspection_fixture(tmp_path)

    result = run_pyepubcheck("images", packaged, "--largest", "2", transport="subprocess")

    assert result.returncode == 0
    assert "OPS/images/cover.png" in result.stdout
    assert "PNG" in result.stdout
    assert "2400x3600" in result.stdout
    assert "OPS/images/figure.jpg" in result.stdout
    assert "JPEG" in result.stdout


def test_metadata_json_reports_stored_metadata_without_validation(run_pyepubcheck, tmp_path: Path) -> None:
    expanded, _packaged = _build_inspection_fixture(tmp_path)

    result = run_pyepubcheck("metadata", expanded, "--format", "json", transport="subprocess")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["packages"][0]["version"] == "3.0"
    assert payload["packages"][0]["uniqueIdentifierValue"] == "urn:uuid:test-book"
    assert any(entry["name"] == "title" and entry["value"] == "Inspection Fixture" for entry in payload["metadata"])
    assert any(entry["name"] == "language" and entry["value"] == "en" for entry in payload["metadata"])


def test_manifest_csv_and_stats_estimates(run_pyepubcheck, tmp_path: Path) -> None:
    _expanded, packaged = _build_inspection_fixture(tmp_path)

    manifest_result = run_pyepubcheck("manifest", packaged, "--format", "csv", transport="subprocess")
    stats_result = run_pyepubcheck(
        "stats", packaged, "--estimate-pages", "--words-per-page", "5", transport="subprocess"
    )

    assert manifest_result.returncode == 0
    assert manifest_result.stdout.startswith("id,href,path,media_type")
    assert "cover,images/cover.png,OPS/images/cover.png,image/png,True" in manifest_result.stdout
    assert stats_result.returncode == 0
    assert "Word count:" in stats_result.stdout
    assert "Estimated pages:" in stats_result.stdout


def test_check_summary_controls_and_read_only_behavior(run_pyepubcheck, tmp_path: Path) -> None:
    _expanded, packaged = _build_inspection_fixture(tmp_path)
    before = _sha256(packaged)

    default_result = run_pyepubcheck(packaged, transport="subprocess")
    no_summary_result = run_pyepubcheck("check", packaged, "--no-summary", transport="subprocess")
    after = _sha256(packaged)

    assert default_result.returncode == 0
    assert "Publication summary" in default_result.stdout
    assert "Inspection Fixture" in default_result.stdout
    assert no_summary_result.returncode == 0
    assert "Publication summary" not in no_summary_result.stdout
    assert before == after
