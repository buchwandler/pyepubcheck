from __future__ import annotations

import struct
from pathlib import Path

from pyepubcheck.inspect import inspect_images, probe_image_bytes


def _make_png(width: int, height: int) -> bytes:
    return (
        b"\x89PNG\r\n\x1a\n"
        + b"\x00\x00\x00\rIHDR"
        + struct.pack(">II", width, height)
        + b"\x08\x02\x00\x00\x00"
        + b"\x00\x00\x00\x00"
    )


def _make_gif(width: int, height: int) -> bytes:
    return b"GIF89a" + struct.pack("<HH", width, height) + b"\x00" * 10


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


def test_probe_png_dimensions() -> None:
    result = probe_image_bytes(_make_png(2400, 3600), media_type="image/png")
    assert result.format == "PNG"
    assert (result.width, result.height) == (2400, 3600)


def test_probe_jpeg_dimensions() -> None:
    result = probe_image_bytes(_make_jpeg(1800, 2700), media_type="image/jpeg")
    assert result.format == "JPEG"
    assert (result.width, result.height) == (1800, 2700)


def test_probe_gif_dimensions() -> None:
    result = probe_image_bytes(_make_gif(640, 480), media_type="image/gif")
    assert result.format == "GIF"
    assert (result.width, result.height) == (640, 480)


def test_probe_svg_viewbox() -> None:
    result = probe_image_bytes(
        b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 200"></svg>',
        media_type="image/svg+xml",
    )
    assert result.format == "SVG"
    assert result.width is None
    assert result.height is None
    assert result.extra["viewBox"] == "0 0 100 200"


def test_inspect_images_collects_reference_information(tmp_path: Path) -> None:
    root = tmp_path / "book"
    (root / "META-INF").mkdir(parents=True)
    (root / "OPS" / "images").mkdir(parents=True)
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
    <dc:title>Image Test</dc:title>
    <dc:language>en</dc:language>
  </metadata>
  <manifest>
    <item id="chapter" href="chapter.xhtml" media-type="application/xhtml+xml"/>
    <item id="styles" href="styles.css" media-type="text/css"/>
    <item id="cover" href="images/cover.png" media-type="image/png" properties="cover-image"/>
    <item id="figure" href="images/figure.jpg" media-type="image/jpeg"/>
  </manifest>
  <spine>
    <itemref idref="chapter"/>
  </spine>
</package>
""",
        encoding="utf-8",
    )
    (root / "OPS" / "chapter.xhtml").write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
  <body>
    <img src="images/cover.png" alt="cover" />
  </body>
</html>
""",
        encoding="utf-8",
    )
    (root / "OPS" / "styles.css").write_text("body { background-image: url('images/figure.jpg'); }", encoding="utf-8")
    (root / "OPS" / "images" / "cover.png").write_bytes(_make_png(2400, 3600))
    (root / "OPS" / "images" / "figure.jpg").write_bytes(_make_jpeg(1200, 800))

    images = inspect_images(root)

    assert any(
        image.id == "cover" and image.width == 2400 and "OPS/chapter.xhtml" in image.referenced_by for image in images
    )
    assert any(
        image.id == "figure" and image.height == 800 and "OPS/styles.css" in image.referenced_by for image in images
    )
