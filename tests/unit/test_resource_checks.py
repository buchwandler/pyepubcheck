"""Unit tests for resource reference checks."""

from __future__ import annotations

from pathlib import Path

import pytest

from pyepubcheck.checks.resources import (
    _is_data_url,
    _is_remote_url,
    _validate_href_format,
    _validate_meta_inf_resources,
    _validate_resource_references,
    run,
)
from pyepubcheck.opf_parser import parse_opf


class TestIsRemoteUrl:
    """Test remote URL detection."""

    def test_http_url(self) -> None:
        assert _is_remote_url("http://example.com/file.xhtml") is True

    def test_https_url(self) -> None:
        assert _is_remote_url("https://example.com/file.xhtml") is True

    def test_relative_path(self) -> None:
        assert _is_remote_url("file.xhtml") is False

    def test_absolute_path(self) -> None:
        assert _is_remote_url("/path/to/file.xhtml") is False

    def test_data_url(self) -> None:
        assert _is_remote_url("data:image/png;base64,abc") is False


class TestIsDataUrl:
    """Test data URL detection."""

    def test_data_url(self) -> None:
        assert _is_data_url("data:image/png;base64,abc") is True

    def test_http_url(self) -> None:
        assert _is_data_url("http://example.com") is False

    def test_relative_path(self) -> None:
        assert _is_data_url("file.xhtml") is False


class TestValidateHrefFormat:
    """Test href format validation."""

    def test_valid_href(self, tmp_path: Path) -> None:
        errors = _validate_href_format(tmp_path / "test.opf", "file.xhtml")
        assert len(errors) == 0

    def test_href_with_spaces(self, tmp_path: Path) -> None:
        errors = _validate_href_format(tmp_path / "test.opf", "my file.xhtml")
        assert len(errors) == 1
        assert errors[0].id == "RSC-007"


class TestValidateResourceReferences:
    """Test resource reference validation."""

    def test_valid_references(self, tmp_path: Path) -> None:
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
        errors = _validate_resource_references(opf_file, opf)
        assert len(errors) == 0

    def test_remote_url_allowed(self, tmp_path: Path) -> None:
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
    <item id="remote" href="https://example.com/font.ttf" media-type="font/ttf"/>
  </manifest>
  <spine/>
</package>"""
        )
        opf = parse_opf(opf_file)
        errors = _validate_resource_references(opf_file, opf)
        assert len(errors) == 0

    def test_data_url_allowed(self, tmp_path: Path) -> None:
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
    <item id="data" href="data:image/png;base64,abc" media-type="image/png"/>
  </manifest>
  <spine/>
</package>"""
        )
        opf = parse_opf(opf_file)
        errors = _validate_resource_references(opf_file, opf)
        assert len(errors) == 0


class TestValidateMetaInfResources:
    """Test META-INF resource validation."""

    def test_no_meta_inf_resources(self, tmp_path: Path) -> None:
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
        errors = _validate_meta_inf_resources(opf_file, opf)
        assert len(errors) == 0

    def test_meta_inf_resource_error(self, tmp_path: Path) -> None:
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
    <item id="meta" href="META-INF/image.png" media-type="image/png"/>
  </manifest>
  <spine>
    <itemref idref="content"/>
  </spine>
</package>"""
        )
        opf = parse_opf(opf_file)
        errors = _validate_meta_inf_resources(opf_file, opf)
        assert len(errors) == 1
        assert errors[0].id == "PKG-025"


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

    def test_non_opf_file(self, tmp_path: Path) -> None:
        xhtml_file = tmp_path / "test.xhtml"
        xhtml_file.write_text("<html/>")
        errors = run(xhtml_file)
        assert len(errors) == 0
