"""Unit tests for SVG checks."""

from __future__ import annotations

from pathlib import Path

from lxml import etree

from pyepubcheck.checks.svg import (
    _validate_svg_ids,
    _validate_svg_use_href,
    run,
)


# specmason: @scenario-EPUBCHECK-RSC-015
class TestValidateSvgUseHref:
    """Test SVG use element href validation."""

    def test_valid_use_href(self, tmp_path: Path) -> None:
        """Test valid SVG use element href."""
        svg_xml = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg">
  <defs><rect id="rect1" width="100" height="100"/></defs>
  <use href="#rect1"/>
</svg>"""
        root = etree.fromstring(svg_xml.encode())
        errors = _validate_svg_use_href(tmp_path / "test.svg", root)
        assert len(errors) == 0

    def test_use_href_no_fragment(self, tmp_path: Path) -> None:
        """Test SVG use element href without fragment."""
        svg_xml = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg">
  <use href="other.svg"/>
</svg>"""
        root = etree.fromstring(svg_xml.encode())
        errors = _validate_svg_use_href(tmp_path / "test.svg", root)
        assert len(errors) == 1
        assert errors[0].id == "RSC-015"


# specmason: @scenario-EPUBCHECK-RSC-005-SVG-ID
class TestValidateSvgIds:
    """Test SVG ID uniqueness validation."""

    def test_unique_ids(self, tmp_path: Path) -> None:
        """Test SVG with unique IDs."""
        svg_xml = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg">
  <rect id="rect1" width="100" height="100"/>
  <rect id="rect2" width="100" height="100"/>
</svg>"""
        root = etree.fromstring(svg_xml.encode())
        errors = _validate_svg_ids(tmp_path / "test.svg", root)
        assert len(errors) == 0

    def test_duplicate_ids(self, tmp_path: Path) -> None:
        """Test SVG with duplicate IDs."""
        svg_xml = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg">
  <rect id="rect1" width="100" height="100"/>
  <rect id="rect1" width="100" height="100"/>
</svg>"""
        root = etree.fromstring(svg_xml.encode())
        errors = _validate_svg_ids(tmp_path / "test.svg", root)
        assert len(errors) == 1
        assert errors[0].id == "RSC-005"
        assert "Duplicate ID: 'rect1'" in errors[0].message


# specmason: @scenario-EPUBCHECK-SVG-RUN
class TestRun:
    """Test run function."""

    def test_valid_svg(self, tmp_path: Path) -> None:
        """Test valid SVG file."""
        svg_file = tmp_path / "test.svg"
        svg_file.write_text("""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg">
  <rect id="rect1" width="100" height="100"/>
</svg>""")
        errors = run(svg_file)
        assert len(errors) == 0

    def test_non_svg_file(self, tmp_path: Path) -> None:
        """Test non-SVG file returns no errors."""
        xhtml_file = tmp_path / "test.xhtml"
        xhtml_file.write_text("<html/>")
        errors = run(xhtml_file)
        assert len(errors) == 0
