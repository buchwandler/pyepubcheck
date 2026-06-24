"""Unit tests for package document checks."""

from __future__ import annotations

from pathlib import Path

import pytest

from pyepubcheck.checks.package import (
    _validate_a11y_properties,
    _validate_collection_metadata,
    _validate_data_nav,
    _validate_href_spaces,
    _validate_prefix_attribute,
    _validate_rendition_layout,
    run,
)
from pyepubcheck.opf_parser import parse_opf


# specmason: @scenario-EPUBCHECK-CFF9E70D
class TestValidateRenditionLayout:
    """Test rendition layout validation."""

    def test_valid_layout_reflowable(self, tmp_path: Path) -> None:
        errors = _validate_rendition_layout(tmp_path / "test.opf", "reflowable")
        assert len(errors) == 0

    def test_valid_layout_pre_paginated(self, tmp_path: Path) -> None:
        errors = _validate_rendition_layout(tmp_path / "test.opf", "pre-paginated")
        assert len(errors) == 0

    def test_invalid_layout(self, tmp_path: Path) -> None:
        errors = _validate_rendition_layout(tmp_path / "test.opf", "invalid")
        assert len(errors) == 1
        assert errors[0].id == "RSC-005"

    def test_empty_layout(self, tmp_path: Path) -> None:
        errors = _validate_rendition_layout(tmp_path / "test.opf", "")
        assert len(errors) == 0


# specmason: @scenario-EPUBCHECK-BD7F26EB
class TestValidatePrefixAttribute:
    """Test prefix attribute validation."""

    def test_valid_prefix(self, tmp_path: Path) -> None:
        errors = _validate_prefix_attribute(tmp_path / "test.opf", "foaf: http://xmlns.com/foaf/spec/")
        assert len(errors) == 0

    def test_valid_multiple_prefixes(self, tmp_path: Path) -> None:
        errors = _validate_prefix_attribute(
            tmp_path / "test.opf",
            "foaf: http://xmlns.com/foaf/spec/ schema: http://schema.org/"
        )
        assert len(errors) == 0

    def test_invalid_syntax_missing_uri(self, tmp_path: Path) -> None:
        errors = _validate_prefix_attribute(tmp_path / "test.opf", "foaf:")
        assert len(errors) > 0

    def test_empty_prefix(self, tmp_path: Path) -> None:
        errors = _validate_prefix_attribute(tmp_path / "test.opf", "")
        assert len(errors) == 0


# specmason: @scenario-EPUBCHECK-F00AF292
class TestValidateHrefSpaces:
    """Test href space validation."""

    def test_no_spaces(self, tmp_path: Path) -> None:
        opf_file = tmp_path / "test.opf"
        opf_file.write_text(
            """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345</dc:identifier>
    <dc:title>Test Book</dc:title>
    <dc:language>en</dc:language>
  </metadata>
  <manifest>
    <item id="content" href="content.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine>
    <itemref idref="content"/>
  </spine>
</package>"""
        )
        opf = parse_opf(opf_file)
        errors = _validate_href_spaces(opf_file, opf)
        assert len(errors) == 0

    def test_with_spaces(self, tmp_path: Path) -> None:
        opf_file = tmp_path / "test.opf"
        opf_file.write_text(
            """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345</dc:identifier>
    <dc:title>Test Book</dc:title>
    <dc:language>en</dc:language>
  </metadata>
  <manifest>
    <item id="content" href="my content.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine>
    <itemref idref="content"/>
  </spine>
</package>"""
        )
        opf = parse_opf(opf_file)
        errors = _validate_href_spaces(opf_file, opf)
        assert len(errors) == 1
        assert errors[0].id == "PKG-010"


class TestValidateDataNav:
    """Test data navigation document validation."""

    def test_valid_nav(self, tmp_path: Path) -> None:
        opf_file = tmp_path / "test.opf"
        opf_file.write_text(
            """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345</dc:identifier>
    <dc:title>Test Book</dc:title>
    <dc:language>en</dc:language>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
  </manifest>
  <spine>
    <itemref idref="nav"/>
  </spine>
</package>"""
        )
        opf = parse_opf(opf_file)
        errors = _validate_data_nav(opf_file, opf)
        assert len(errors) == 0

    def test_invalid_nav_media_type(self, tmp_path: Path) -> None:
        opf_file = tmp_path / "test.opf"
        opf_file.write_text(
            """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345</dc:identifier>
    <dc:title>Test Book</dc:title>
    <dc:language>en</dc:language>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="text/html" properties="nav"/>
  </manifest>
  <spine>
    <itemref idref="nav"/>
  </spine>
</package>"""
        )
        opf = parse_opf(opf_file)
        errors = _validate_data_nav(opf_file, opf)
        assert len(errors) == 1
        assert errors[0].id == "OPF-012"


class TestRun:
    """Test run function."""

    def test_valid_opf(self, tmp_path: Path) -> None:
        opf_file = tmp_path / "test.opf"
        opf_file.write_text(
            """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345</dc:identifier>
    <dc:title>Test Book</dc:title>
    <dc:language>en</dc:language>
  </metadata>
  <manifest>
    <item id="content" href="content.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine>
    <itemref idref="content"/>
  </spine>
</package>"""
        )
        errors = run(opf_file)
        assert len(errors) == 0

    def test_missing_identifier(self, tmp_path: Path) -> None:
        opf_file = tmp_path / "test.opf"
        opf_file.write_text(
            """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title>Test Book</dc:title>
    <dc:language>en</dc:language>
  </metadata>
  <manifest>
    <item id="content" href="content.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine>
    <itemref idref="content"/>
  </spine>
</package>"""
        )
        errors = run(opf_file)
        assert any(e.id == "RSC-005" and "identifier" in e.message for e in errors)

    def test_missing_title(self, tmp_path: Path) -> None:
        opf_file = tmp_path / "test.opf"
        opf_file.write_text(
            """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345</dc:identifier>
    <dc:language>en</dc:language>
  </metadata>
  <manifest>
    <item id="content" href="content.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine>
    <itemref idref="content"/>
  </spine>
</package>"""
        )
        errors = run(opf_file)
        assert any(e.id == "RSC-005" and "title" in e.message for e in errors)

    def test_undeclared_prefix(self, tmp_path: Path) -> None:
        opf_file = tmp_path / "test.opf"
        opf_file.write_text(
            """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345</dc:identifier>
    <dc:title>Test Book</dc:title>
    <dc:language>en</dc:language>
  </metadata>
  <manifest>
    <item id="content" href="content.xhtml" media-type="application/xhtml+xml" properties="prism:test"/>
  </manifest>
  <spine>
    <itemref idref="content"/>
  </spine>
</package>"""
        )
        errors = run(opf_file)
        assert any(e.id == "OPF-028" and "prism" in e.message for e in errors)

    def test_invalid_rendition_layout(self, tmp_path: Path) -> None:
        opf_file = tmp_path / "test.opf"
        opf_file.write_text(
            """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345</dc:identifier>
    <dc:title>Test Book</dc:title>
    <dc:language>en</dc:language>
    <meta property="rendition:layout">invalid</meta>
  </metadata>
  <manifest>
    <item id="content" href="content.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine>
    <itemref idref="content"/>
  </spine>
</package>"""
        )
        errors = run(opf_file)
        assert any(e.id == "RSC-005" and "rendition:layout" in e.message for e in errors)

    def test_non_opf_file(self, tmp_path: Path) -> None:
        xhtml_file = tmp_path / "test.xhtml"
        xhtml_file.write_text(
            """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Test</title></head>
<body/>
</html>"""
        )
        # Non-OPF files should be skipped
        errors = run(xhtml_file)
        assert len(errors) == 0
