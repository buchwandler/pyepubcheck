"""Unit tests for OPF parser."""

from __future__ import annotations

from pathlib import Path

import pytest

from pyepubcheck.opf_parser import (
    ManifestItem,
    OpfDocument,
    PrefixDeclaration,
    SpineItemref,
    parse_opf,
    parse_prefix_attribute,
    validate_opf_prefixes,
    validate_opf_required_metadata,
)


# specmason: @scenario-EPUBCHECK-BD7F26EB
class TestParsePrefixAttribute:
    """Test prefix attribute parsing."""

    def test_single_prefix(self) -> None:
        result = parse_prefix_attribute("foaf: http://xmlns.com/foaf/spec/")
        assert len(result) == 1
        assert result[0].prefix == "foaf"
        assert result[0].uri == "http://xmlns.com/foaf/spec/"

    def test_multiple_prefixes(self) -> None:
        result = parse_prefix_attribute(
            "foaf: http://xmlns.com/foaf/spec/ schema: http://schema.org/"
        )
        assert len(result) == 2
        assert result[0].prefix == "foaf"
        assert result[1].prefix == "schema"

    def test_empty_string(self) -> None:
        result = parse_prefix_attribute("")
        assert len(result) == 0


# specmason: @scenario-EPUBCHECK-13027092
class TestParseOpf:
    """Test OPF document parsing."""

    def test_minimal_opf(self, tmp_path: Path) -> None:
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
    <item id="content" href="content.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine>
    <itemref idref="content"/>
  </spine>
</package>"""
        )
        opf = parse_opf(opf_file)
        assert len(opf.errors) == 0
        assert opf.version == "3.0"
        assert opf.unique_identifier == "uid"
        assert len(opf.metadata.identifiers) == 1
        assert opf.metadata.identifiers[0] == "urn:uuid:12345"
        assert len(opf.metadata.titles) == 1
        assert opf.metadata.titles[0] == "Test Book"
        assert len(opf.metadata.languages) == 1
        assert opf.metadata.languages[0] == "en"

    def test_manifest_parsing(self, tmp_path: Path) -> None:
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
    <item id="content" href="content.xhtml" media-type="application/xhtml+xml"/>
    <item id="css" href="style.css" media-type="text/css"/>
  </manifest>
  <spine>
    <itemref idref="content"/>
  </spine>
</package>"""
        )
        opf = parse_opf(opf_file)
        assert len(opf.manifest) == 3
        assert opf.manifest[0].id == "nav"
        assert opf.manifest[0].properties == ["nav"]
        assert opf.manifest[1].id == "content"
        assert opf.manifest[2].id == "css"
        assert opf.manifest[2].media_type == "text/css"

    def test_spine_parsing(self, tmp_path: Path) -> None:
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
    <item id="ch1" href="ch1.xhtml" media-type="application/xhtml+xml"/>
    <item id="ch2" href="ch2.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine toc="nav">
    <itemref idref="ch1"/>
    <itemref idref="ch2" linear="no"/>
  </spine>
</package>"""
        )
        opf = parse_opf(opf_file)
        assert opf.spine_toc == "nav"
        assert len(opf.spine) == 2
        assert opf.spine[0].idref == "ch1"
        assert opf.spine[0].linear is True
        assert opf.spine[1].idref == "ch2"
        assert opf.spine[1].linear is False

    def test_prefix_parsing(self, tmp_path: Path) -> None:
        opf_file = tmp_path / "test.opf"
        opf_file.write_text(
            """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid"
         prefix="foaf: http://xmlns.com/foaf/spec/">
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
        assert len(opf.prefixes) == 1
        assert opf.prefixes[0].prefix == "foaf"

    def test_rendition_metadata(self, tmp_path: Path) -> None:
        opf_file = tmp_path / "test.opf"
        opf_file.write_text(
            """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345</dc:identifier>
    <dc:title>Test Book</dc:title>
    <dc:language>en</dc:language>
    <meta property="dcterms:modified">2024-01-01T00:00:00Z</meta>
    <meta property="rendition:layout">pre-paginated</meta>
    <meta property="rendition:orientation">portrait</meta>
    <meta property="rendition:spread">none</meta>
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
        assert opf.metadata.modified == "2024-01-01T00:00:00Z"
        assert opf.metadata.rendition_layout == "pre-paginated"
        assert opf.metadata.rendition_orientation == "portrait"
        assert opf.metadata.rendition_spread == "none"

    def test_invalid_xml(self, tmp_path: Path) -> None:
        opf_file = tmp_path / "test.opf"
        opf_file.write_text("not xml")
        opf = parse_opf(opf_file)
        assert len(opf.errors) == 1
        assert opf.errors[0].id == "RSC-005"

    def test_manifest_by_id(self, tmp_path: Path) -> None:
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
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml"/>
    <item id="content" href="content.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine>
    <itemref idref="content"/>
  </spine>
</package>"""
        )
        opf = parse_opf(opf_file)
        assert "nav" in opf.manifest_by_id
        assert "content" in opf.manifest_by_id
        assert opf.get_manifest_item("nav") is not None
        assert opf.get_manifest_item("missing") is None


class TestValidateOpfRequiredMetadata:
    """Test required metadata validation."""

    def test_valid_metadata(self, tmp_path: Path) -> None:
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
        errors = validate_opf_required_metadata(opf)
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
        opf = parse_opf(opf_file)
        errors = validate_opf_required_metadata(opf)
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
        opf = parse_opf(opf_file)
        errors = validate_opf_required_metadata(opf)
        assert any(e.id == "RSC-005" and "title" in e.message for e in errors)

    def test_missing_language(self, tmp_path: Path) -> None:
        opf_file = tmp_path / "test.opf"
        opf_file.write_text(
            """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345</dc:identifier>
    <dc:title>Test Book</dc:title>
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
        errors = validate_opf_required_metadata(opf)
        assert any(e.id == "RSC-005" and "language" in e.message for e in errors)


class TestValidateOpfPrefixes:
    """Test prefix validation."""

    def test_valid_prefixes(self, tmp_path: Path) -> None:
        opf_file = tmp_path / "test.opf"
        opf_file.write_text(
            """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid"
         prefix="foaf: http://xmlns.com/foaf/spec/">
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
        errors = validate_opf_prefixes(opf)
        assert len(errors) == 0

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
        opf = parse_opf(opf_file)
        errors = validate_opf_prefixes(opf)
        assert any(e.id == "OPF-028" and "prism" in e.message for e in errors)
