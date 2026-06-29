"""Unit tests for XHTML validator."""

from __future__ import annotations

from pathlib import Path

from lxml import etree

from pyepubcheck.xhtml_validator import (
    validate_xhtml_alt_attributes,
    validate_xhtml_duplicate_ids,
    validate_xhtml_resource_references,
    validate_xhtml_style_elements,
)


# specmason: @scenario-EPUBCHECK-RSC-005-DUPLICATE-ID
class TestValidateXhtmlDuplicateIds:
    """Test duplicate ID validation."""

    def test_no_duplicate_ids(self) -> None:
        """Test XHTML with no duplicate IDs."""
        xhtml_xml = """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Test</title></head>
<body>
  <p id="p1">Paragraph 1</p>
  <p id="p2">Paragraph 2</p>
</body>
</html>"""
        root = etree.fromstring(xhtml_xml.encode())
        errors = validate_xhtml_duplicate_ids(Path("test.xhtml"), root)
        assert len(errors) == 0

    def test_duplicate_ids(self) -> None:
        """Test XHTML with duplicate IDs."""
        xhtml_xml = """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Test</title></head>
<body>
  <p id="p1">Paragraph 1</p>
  <p id="p1">Paragraph 2</p>
</body>
</html>"""
        root = etree.fromstring(xhtml_xml.encode())
        errors = validate_xhtml_duplicate_ids(Path("test.xhtml"), root)
        assert len(errors) == 1
        assert errors[0].id == "RSC-005"
        assert "duplicate ID 'p1'" in errors[0].message


# specmason: @scenario-EPUBCHECK-RSC-005-ALT
class TestValidateXhtmlAltAttributes:
    """Test alt attribute validation."""

    def test_img_with_alt(self) -> None:
        """Test img element with alt attribute."""
        xhtml_xml = """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Test</title></head>
<body>
  <img src="image.png" alt="Description"/>
</body>
</html>"""
        root = etree.fromstring(xhtml_xml.encode())
        errors = validate_xhtml_alt_attributes(Path("test.xhtml"), root)
        assert len(errors) == 0

    def test_img_without_alt(self) -> None:
        """Test img element without alt attribute."""
        xhtml_xml = """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Test</title></head>
<body>
  <img src="image.png"/>
</body>
</html>"""
        root = etree.fromstring(xhtml_xml.encode())
        errors = validate_xhtml_alt_attributes(Path("test.xhtml"), root)
        assert len(errors) == 1
        assert errors[0].id == "RSC-005"
        assert "img element missing alt attribute" in errors[0].message


# specmason: @scenario-EPUBCHECK-RSC-007-RESOURCE
class TestValidateXhtmlResourceReferences:
    """Test resource reference validation."""

    def test_valid_resource_reference(self) -> None:
        """Test valid resource reference."""
        xhtml_xml = """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Test</title></head>
<body>
  <img src="image.png" alt="Test"/>
</body>
</html>"""
        root = etree.fromstring(xhtml_xml.encode())
        manifest_items = {"image.png"}
        errors = validate_xhtml_resource_references(
            Path("test.xhtml"), root, manifest_items
        )
        assert len(errors) == 0

    def test_missing_resource_reference(self) -> None:
        """Test missing resource reference."""
        xhtml_xml = """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Test</title></head>
<body>
  <img src="missing.png" alt="Test"/>
</body>
</html>"""
        root = etree.fromstring(xhtml_xml.encode())
        manifest_items: set[str] = set()
        errors = validate_xhtml_resource_references(
            Path("test.xhtml"), root, manifest_items
        )
        assert len(errors) == 1
        assert errors[0].id == "RSC-007"
        assert (
            "referenced resource 'missing.png' not found in manifest"
            in errors[0].message
        )

    def test_remote_resource_allowed(self) -> None:
        """Test remote resource reference is allowed."""
        xhtml_xml = """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Test</title></head>
<body>
  <img src="https://example.com/image.png" alt="Test"/>
</body>
</html>"""
        root = etree.fromstring(xhtml_xml.encode())
        manifest_items: set[str] = set()
        errors = validate_xhtml_resource_references(
            Path("test.xhtml"), root, manifest_items
        )
        assert len(errors) == 0


# specmason: @scenario-EPUBCHECK-RSC-005-STYLE
class TestValidateXhtmlStyleElements:
    """Test style element validation."""

    def test_style_element_allowed(self) -> None:
        """Test that style elements are allowed."""
        xhtml_xml = """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>Test</title>
  <style type="text/css">body { color: red; }</style>
</head>
<body><p>Content</p></body>
</html>"""
        root = etree.fromstring(xhtml_xml.encode())
        errors = validate_xhtml_style_elements(Path("test.xhtml"), root)
        assert len(errors) == 0
