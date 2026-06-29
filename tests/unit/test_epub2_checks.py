"""Unit tests for EPUB 2 checks."""

from __future__ import annotations

from pathlib import Path

from pyepubcheck.checks.epub2 import (
    _validate_fallbacks,
    _validate_manifest_items,
    _validate_ncx_ids,
    _validate_ncx_resources,
    _validate_ncx_uid,
    _validate_remote_objects,
    _validate_spine_toc,
    _validate_unique_identifier,
    _validate_xhtml_namespace,
    run,
)


# specmason: @scenario-EPUBCHECK-OPF-030
class TestValidateUniqueIdentifier:
    """Test unique identifier validation."""

    def test_valid_unique_identifier(self, tmp_path: Path) -> None:
        """Test valid unique identifier reference."""
        opf_content = """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="uid" version="2.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345</dc:identifier>
  </metadata>
  <manifest/>
  <spine/>
</package>"""
        opf_file = tmp_path / "test.opf"
        opf_file.write_text(opf_content)

        from pyepubcheck.opf_parser import parse_opf
        opf = parse_opf(opf_file)
        errors = _validate_unique_identifier(opf_file, opf)
        assert len(errors) == 0

    def test_missing_unique_identifier(self, tmp_path: Path) -> None:
        """Test missing unique identifier reference."""
        opf_content = """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="uid" version="2.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="other">urn:uuid:12345</dc:identifier>
  </metadata>
  <manifest/>
  <spine/>
</package>"""
        opf_file = tmp_path / "test.opf"
        opf_file.write_text(opf_content)

        from pyepubcheck.opf_parser import parse_opf
        opf = parse_opf(opf_file)
        errors = _validate_unique_identifier(opf_file, opf)
        assert len(errors) == 1
        assert errors[0].id == "OPF-030"


# specmason: @scenario-EPUBCHECK-OPF-003
class TestValidateSpineToc:
    """Test spine toc validation."""

    def test_valid_spine_toc(self, tmp_path: Path) -> None:
        """Test valid spine toc attribute."""
        opf_content = """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345</dc:identifier>
  </metadata>
  <manifest>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
  </manifest>
  <spine toc="ncx"/>
</package>"""
        opf_file = tmp_path / "test.opf"
        opf_file.write_text(opf_content)

        from pyepubcheck.opf_parser import parse_opf
        opf = parse_opf(opf_file)
        errors = _validate_spine_toc(opf_file, opf)
        assert len(errors) == 0

    def test_missing_spine_toc_with_ncx(self, tmp_path: Path) -> None:
        """Test missing spine toc when NCX is present."""
        opf_content = """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345</dc:identifier>
  </metadata>
  <manifest>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
  </manifest>
  <spine/>
</package>"""
        opf_file = tmp_path / "test.opf"
        opf_file.write_text(opf_content)

        from pyepubcheck.opf_parser import parse_opf
        opf = parse_opf(opf_file)
        errors = _validate_spine_toc(opf_file, opf)
        assert len(errors) == 1
        assert errors[0].id == "OPF-003"

    def test_spine_toc_not_ncx(self, tmp_path: Path) -> None:
        """Test spine toc pointing to non-NCX item."""
        opf_content = """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345</dc:identifier>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine toc="nav"/>
</package>"""
        opf_file = tmp_path / "test.opf"
        opf_file.write_text(opf_content)

        from pyepubcheck.opf_parser import parse_opf
        opf = parse_opf(opf_file)
        errors = _validate_spine_toc(opf_file, opf)
        assert len(errors) == 1
        assert errors[0].id == "RSC-005"


# specmason: @scenario-EPUBCHECK-RSC-007 @scenario-EPUBCHECK-RSC-001
class TestValidateManifestItems:
    """Test manifest item validation."""

    def test_valid_manifest_items(self, tmp_path: Path) -> None:
        """Test valid manifest items."""
        opf_content = """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345</dc:identifier>
  </metadata>
  <manifest>
    <item id="content" href="content.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine/>
</package>"""
        opf_file = tmp_path / "test.opf"
        opf_file.write_text(opf_content)

        from pyepubcheck.opf_parser import parse_opf
        opf = parse_opf(opf_file)
        errors = _validate_manifest_items(opf_file, opf)
        assert len(errors) == 0

    def test_missing_item_id(self, tmp_path: Path) -> None:
        """Test manifest item missing id."""
        opf_content = """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345</dc:identifier>
  </metadata>
  <manifest>
    <item href="content.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine/>
</package>"""
        opf_file = tmp_path / "test.opf"
        opf_file.write_text(opf_content)

        from pyepubcheck.opf_parser import parse_opf
        opf = parse_opf(opf_file)
        errors = _validate_manifest_items(opf_file, opf)
        assert len(errors) == 1
        assert errors[0].id == "RSC-005"

    def test_missing_item_href(self, tmp_path: Path) -> None:
        """Test manifest item missing href."""
        opf_content = """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345</dc:identifier>
  </metadata>
  <manifest>
    <item id="content" media-type="application/xhtml+xml"/>
  </manifest>
  <spine/>
</package>"""
        opf_file = tmp_path / "test.opf"
        opf_file.write_text(opf_content)

        from pyepubcheck.opf_parser import parse_opf
        opf = parse_opf(opf_file)
        errors = _validate_manifest_items(opf_file, opf)
        assert len(errors) == 1
        assert errors[0].id == "RSC-007"

    def test_missing_item_media_type(self, tmp_path: Path) -> None:
        """Test manifest item missing media-type."""
        opf_content = """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345</dc:identifier>
  </metadata>
  <manifest>
    <item id="content" href="content.xhtml"/>
  </manifest>
  <spine/>
</package>"""
        opf_file = tmp_path / "test.opf"
        opf_file.write_text(opf_content)

        from pyepubcheck.opf_parser import parse_opf
        opf = parse_opf(opf_file)
        errors = _validate_manifest_items(opf_file, opf)
        assert len(errors) == 1
        assert errors[0].id == "RSC-005"


# specmason: @scenario-EPUBCHECK-OPF-040
class TestValidateFallbacks:
    """Test fallback validation."""

    def test_valid_fallback(self, tmp_path: Path) -> None:
        """Test valid fallback reference."""
        opf_content = """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345</dc:identifier>
  </metadata>
  <manifest>
    <item id="content" href="content.xhtml" media-type="application/xhtml+xml" fallback="fallback"/>
    <item id="fallback" href="fallback.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine/>
</package>"""
        opf_file = tmp_path / "test.opf"
        opf_file.write_text(opf_content)

        from pyepubcheck.opf_parser import parse_opf
        opf = parse_opf(opf_file)
        errors = _validate_fallbacks(opf_file, opf)
        assert len(errors) == 0

    def test_missing_fallback(self, tmp_path: Path) -> None:
        """Test missing fallback reference."""
        opf_content = """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345</dc:identifier>
  </metadata>
  <manifest>
    <item id="content" href="content.xhtml" media-type="application/xhtml+xml" fallback="missing"/>
  </manifest>
  <spine/>
</package>"""
        opf_file = tmp_path / "test.opf"
        opf_file.write_text(opf_content)

        from pyepubcheck.opf_parser import parse_opf
        opf = parse_opf(opf_file)
        errors = _validate_fallbacks(opf_file, opf)
        assert len(errors) == 1
        assert errors[0].id == "OPF-040"


# specmason: @scenario-EPUBCHECK-NCX-002
class TestValidateNcxIds:
    """Test NCX ID validation."""

    def test_no_duplicate_ids(self) -> None:
        """Test NCX with no duplicate IDs."""
        from lxml import etree

        ncx_xml = """<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head/>
  <docTitle><text>Test</text></docTitle>
  <navMap>
    <navPoint id="nav1"><navLabel><text>Chapter 1</text></navLabel><content src="ch1.xhtml"/></navPoint>
    <navPoint id="nav2"><navLabel><text>Chapter 2</text></navLabel><content src="ch2.xhtml"/></navPoint>
  </navMap>
</ncx>"""
        ncx_root = etree.fromstring(ncx_xml.encode())
        errors = _validate_ncx_ids(Path("test.ncx"), ncx_root)
        assert len(errors) == 0

    def test_duplicate_ids(self) -> None:
        """Test NCX with duplicate IDs."""
        from lxml import etree

        ncx_xml = """<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head/>
  <docTitle><text>Test</text></docTitle>
  <navMap>
    <navPoint id="nav1"><navLabel><text>Chapter 1</text></navLabel><content src="ch1.xhtml"/></navPoint>
    <navPoint id="nav1"><navLabel><text>Chapter 2</text></navLabel><content src="ch2.xhtml"/></navPoint>
  </navMap>
</ncx>"""
        ncx_root = etree.fromstring(ncx_xml.encode())
        errors = _validate_ncx_ids(Path("test.ncx"), ncx_root)
        assert len(errors) == 1
        assert errors[0].id == "NCX-002"


# specmason: @scenario-EPUBCHECK-NCX-003
class TestValidateNcxResources:
    """Test NCX resource validation."""

    def test_valid_ncx_resources(self) -> None:
        """Test NCX with valid resource references."""
        from lxml import etree

        ncx_xml = """<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head/>
  <docTitle><text>Test</text></docTitle>
  <navMap>
    <navPoint id="nav1"><navLabel><text>Chapter 1</text></navLabel><content src="ch1.xhtml"/></navPoint>
    <navPoint id="nav2"><navLabel><text>Chapter 2</text></navLabel><content src="ch2.xhtml"/></navPoint>
  </navMap>
</ncx>"""
        ncx_root = etree.fromstring(ncx_xml.encode())
        spine_items = {"ch1.xhtml", "ch2.xhtml"}
        errors = _validate_ncx_resources(Path("test.ncx"), ncx_root, spine_items)
        assert len(errors) == 0

    def test_missing_ncx_resource(self) -> None:
        """Test NCX with missing resource reference."""
        from lxml import etree

        ncx_xml = """<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head/>
  <docTitle><text>Test</text></docTitle>
  <navMap>
    <navPoint id="nav1"><navLabel><text>Chapter 1</text></navLabel><content src="ch1.xhtml"/></navPoint>
    <navPoint id="nav2"><navLabel><text>Chapter 2</text></navLabel><content src="missing.xhtml"/></navPoint>
  </navMap>
</ncx>"""
        ncx_root = etree.fromstring(ncx_xml.encode())
        spine_items = {"ch1.xhtml"}
        errors = _validate_ncx_resources(Path("test.ncx"), ncx_root, spine_items)
        assert len(errors) == 1
        assert errors[0].id == "NCX-003"


# specmason: @scenario-EPUBCHECK-NCX-004
class TestValidateNcxUid:
    """Test NCX UID validation."""

    def test_matching_uid(self) -> None:
        """Test NCX with matching UID."""
        from lxml import etree

        ncx_xml = """<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="urn:uuid:12345"/>
  </head>
  <docTitle><text>Test</text></docTitle>
  <navMap/>
</ncx>"""
        ncx_root = etree.fromstring(ncx_xml.encode())
        errors = _validate_ncx_uid(Path("test.ncx"), ncx_root, "urn:uuid:12345")
        assert len(errors) == 0

    def test_mismatched_uid(self) -> None:
        """Test NCX with mismatched UID."""
        from lxml import etree

        ncx_xml = """<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="urn:uuid:99999"/>
  </head>
  <docTitle><text>Test</text></docTitle>
  <navMap/>
</ncx>"""
        ncx_root = etree.fromstring(ncx_xml.encode())
        errors = _validate_ncx_uid(Path("test.ncx"), ncx_root, "urn:uuid:12345")
        assert len(errors) == 1
        assert errors[0].id == "NCX-004"


# specmason: @scenario-EPUBCHECK-RSC-005
class TestValidateXhtmlNamespace:
    """Test XHTML namespace validation."""

    def test_valid_xhtml_namespace(self) -> None:
        """Test valid XHTML namespace."""
        from lxml import etree

        xhtml_xml = """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Test</title></head>
<body><p>Content</p></body>
</html>"""
        xhtml_root = etree.fromstring(xhtml_xml.encode())
        errors = _validate_xhtml_namespace(Path("test.xhtml"), xhtml_root)
        assert len(errors) == 0

    def test_invalid_xhtml_namespace(self) -> None:
        """Test invalid XHTML namespace."""
        from lxml import etree

        xhtml_xml = """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/2000/svg">
<head><title>Test</title></head>
<body><p>Content</p></body>
</html>"""
        xhtml_root = etree.fromstring(xhtml_xml.encode())
        errors = _validate_xhtml_namespace(Path("test.xhtml"), xhtml_root)
        assert len(errors) == 1
        assert errors[0].id == "RSC-005"

    def test_missing_xhtml_namespace(self) -> None:
        """Test missing XHTML namespace."""
        from lxml import etree

        xhtml_xml = """<?xml version="1.0" encoding="UTF-8"?>
<html>
<head><title>Test</title></head>
<body><p>Content</p></body>
</html>"""
        xhtml_root = etree.fromstring(xhtml_xml.encode())
        errors = _validate_xhtml_namespace(Path("test.xhtml"), xhtml_root)
        assert len(errors) == 1
        assert errors[0].id == "RSC-005"


# specmason: @scenario-EPUBCHECK-RSC-001
class TestValidateRemoteObjects:
    """Test remote object validation."""

    def test_valid_local_reference(self) -> None:
        """Test valid local reference."""
        from lxml import etree

        xhtml_xml = """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Test</title></head>
<body><img src="image.png" alt="Test"/></body>
</html>"""
        xhtml_root = etree.fromstring(xhtml_xml.encode())
        manifest_items = {"image.png"}
        errors = _validate_remote_objects(Path("test.xhtml"), xhtml_root, manifest_items)
        assert len(errors) == 0

    def test_missing_local_reference(self) -> None:
        """Test missing local reference."""
        from lxml import etree

        xhtml_xml = """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Test</title></head>
<body><img src="missing.png" alt="Test"/></body>
</html>"""
        xhtml_root = etree.fromstring(xhtml_xml.encode())
        manifest_items: set[str] = set()
        errors = _validate_remote_objects(Path("test.xhtml"), xhtml_root, manifest_items)
        assert len(errors) == 1
        assert errors[0].id == "RSC-001"

    def test_remote_reference_allowed(self) -> None:
        """Test remote reference is allowed."""
        from lxml import etree

        xhtml_xml = """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Test</title></head>
<body><img src="https://example.com/image.png" alt="Test"/></body>
</html>"""
        xhtml_root = etree.fromstring(xhtml_xml.encode())
        manifest_items: set[str] = set()
        errors = _validate_remote_objects(Path("test.xhtml"), xhtml_root, manifest_items)
        assert len(errors) == 0


# specmason: @scenario-EPUBCHECK-EPUB2-RUN
class TestRun:
    """Test run function."""

    def test_valid_opf(self, tmp_path: Path) -> None:
        """Test valid OPF file."""
        opf_content = """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="uid" version="2.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:12345</dc:identifier>
    <dc:title>Test</dc:title>
    <dc:language>en</dc:language>
  </metadata>
  <manifest>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
    <item id="content" href="content.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine toc="ncx"/>
</package>"""
        opf_file = tmp_path / "test.opf"
        opf_file.write_text(opf_content)
        errors = run(opf_file)
        assert len(errors) == 0

    def test_non_opf_file(self, tmp_path: Path) -> None:
        """Test non-OPF file returns no errors."""
        xhtml_file = tmp_path / "test.xhtml"
        xhtml_file.write_text("<html/>")
        errors = run(xhtml_file)
        assert len(errors) == 0
