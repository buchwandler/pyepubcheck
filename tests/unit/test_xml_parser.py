"""Unit tests for XML parser."""

from __future__ import annotations

from pathlib import Path

import pytest

from pyepubcheck.xml_parser import (
    XmlDocument,
    detect_doc_type,
    load_xml,
    load_xml_string,
    validate_xml_well_formedness,
)


# specmason: @scenario-EPUBCHECK-2EF4BE8A
class TestDetectDocType:
    """Test document type detection."""

    def test_opf_package(self) -> None:
        from lxml import etree
        root = etree.Element("{http://www.idpf.org/2007/opf}package")
        assert detect_doc_type(root) == "opf"

    def test_xhtml_html(self) -> None:
        from lxml import etree
        root = etree.Element("{http://www.w3.org/1999/xhtml}html")
        assert detect_doc_type(root) == "xhtml"

    def test_xhtml_html_no_ns(self) -> None:
        from lxml import etree
        root = etree.Element("html")
        assert detect_doc_type(root) == "xhtml"

    def test_svg(self) -> None:
        from lxml import etree
        root = etree.Element("{http://www.w3.org/2000/svg}svg")
        assert detect_doc_type(root) == "svg"

    def test_svg_no_ns(self) -> None:
        from lxml import etree
        root = etree.Element("svg")
        assert detect_doc_type(root) == "svg"

    def test_ncx(self) -> None:
        from lxml import etree
        root = etree.Element("{http://www.daisy.org/z3986/2005/ncx/}ncx")
        assert detect_doc_type(root) == "ncx"

    def test_smil(self) -> None:
        from lxml import etree
        root = etree.Element("{http://www.w3.org/ns/SMIL}smil")
        assert detect_doc_type(root) == "smil"

    def test_unknown(self) -> None:
        from lxml import etree
        root = etree.Element("unknown")
        assert detect_doc_type(root) == "unknown"


# specmason: @scenario-EPUBCHECK-A4385CDA
class TestLoadXmlString:
    """Test loading XML from string."""

    def test_valid_xml(self) -> None:
        content = '<?xml version="1.0"?><root><child/></root>'
        doc = load_xml_string(content)
        assert doc.root.tag == "root"
        assert len(doc.errors) == 0

    def test_invalid_xml(self) -> None:
        content = '<?xml version="1.0"?><root><child></root>'
        doc = load_xml_string(content)
        assert len(doc.errors) == 1
        assert doc.errors[0].id == "RSC-005"

    def test_empty_content(self) -> None:
        content = ""
        doc = load_xml_string(content)
        assert len(doc.errors) == 1

    def test_namespace_detection(self) -> None:
        content = '<?xml version="1.0"?><package xmlns="http://www.idpf.org/2007/opf"/>'
        doc = load_xml_string(content)
        assert doc.doc_type == "opf"


# specmason: @scenario-EPUBCHECK-DB777964
class TestXmlDocument:
    """Test XmlDocument methods."""

    def test_find_element(self) -> None:
        content = '<?xml version="1.0"?><root><child attr="value"/></root>'
        doc = load_xml_string(content)
        child = doc.find("child")
        assert child is not None
        assert child.get("attr") == "value"

    def test_find_missing_element(self) -> None:
        content = '<?xml version="1.0"?><root><child/></root>'
        doc = load_xml_string(content)
        missing = doc.find("missing")
        assert missing is None

    def test_findall_elements(self) -> None:
        content = '<?xml version="1.0"?><root><child/><child/></root>'
        doc = load_xml_string(content)
        children = doc.findall("child")
        assert len(children) == 2

    def test_nsmap(self) -> None:
        content = '<?xml version="1.0"?><root xmlns:ns="http://example.com"/>'
        doc = load_xml_string(content)
        assert "ns" in doc.nsmap

    def test_get_attr(self) -> None:
        content = '<?xml version="1.0"?><root><child attr="value"/></root>'
        doc = load_xml_string(content)
        child = doc.find("child")
        assert child is not None
        assert doc.get_attr(child, "attr") == "value"

    def test_get_attr_default(self) -> None:
        content = '<?xml version="1.0"?><root><child/></root>'
        doc = load_xml_string(content)
        child = doc.find("child")
        assert child is not None
        assert doc.get_attr(child, "missing", "default") == "default"


class TestValidateXmlWellFormedness:
    """Test XML well-formedness validation."""

    def test_valid_xml(self, tmp_path: Path) -> None:
        xml_file = tmp_path / "test.xml"
        xml_file.write_text('<?xml version="1.0"?><root/>')
        errors = validate_xml_well_formedness(xml_file)
        assert len(errors) == 0

    def test_invalid_xml(self, tmp_path: Path) -> None:
        xml_file = tmp_path / "test.xml"
        xml_file.write_text('<?xml version="1.0"?><root><child></root>')
        errors = validate_xml_well_formedness(xml_file)
        assert len(errors) == 1
        assert errors[0].id == "RSC-005"

    def test_missing_file(self, tmp_path: Path) -> None:
        xml_file = tmp_path / "missing.xml"
        errors = validate_xml_well_formedness(xml_file)
        assert len(errors) == 1
        assert errors[0].id == "RSC-001"


class TestLoadXml:
    """Test loading XML from file."""

    def test_valid_file(self, tmp_path: Path) -> None:
        xml_file = tmp_path / "test.xml"
        xml_file.write_text('<?xml version="1.0"?><root/>')
        doc = load_xml(xml_file)
        assert doc.root.tag == "root"
        assert len(doc.errors) == 0

    def test_invalid_file(self, tmp_path: Path) -> None:
        xml_file = tmp_path / "test.xml"
        xml_file.write_text('<?xml version="1.0"?><root><child></root>')
        doc = load_xml(xml_file)
        assert len(doc.errors) == 1
        assert doc.errors[0].id == "RSC-005"

    def test_missing_file(self, tmp_path: Path) -> None:
        xml_file = tmp_path / "missing.xml"
        doc = load_xml(xml_file)
        assert len(doc.errors) == 1
        assert doc.errors[0].id == "RSC-001"

    def test_opf_detection(self, tmp_path: Path) -> None:
        xml_file = tmp_path / "test.opf"
        xml_file.write_text('<?xml version="1.0"?><package xmlns="http://www.idpf.org/2007/opf"/>')
        doc = load_xml(xml_file)
        assert doc.doc_type == "opf"

    def test_xhtml_detection(self, tmp_path: Path) -> None:
        xml_file = tmp_path / "test.xhtml"
        xml_file.write_text('<?xml version="1.0"?><html xmlns="http://www.w3.org/1999/xhtml"><head><title>Test</title></head><body/></html>')
        doc = load_xml(xml_file)
        assert doc.doc_type == "xhtml"
