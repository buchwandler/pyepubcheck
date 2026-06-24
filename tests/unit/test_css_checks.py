"""Unit tests for CSS checks."""

from __future__ import annotations

from pathlib import Path

import pytest

from pyepubcheck.checks.css import (
    _validate_css_properties,
    _validate_css_urls,
    _validate_css_direction,
    _validate_css_selectors,
    run,
)


# specmason: @scenario-EPUBCHECK-CSS-001
class TestValidateCssProperties:
    """Test CSS property validation."""

    def test_valid_css(self, tmp_path: Path) -> None:
        """Test valid CSS properties."""
        css_content = "body { color: red; }"
        errors = _validate_css_properties(tmp_path / "test.css", css_content)
        assert len(errors) == 0

    def test_disallowed_property(self, tmp_path: Path) -> None:
        """Test disallowed CSS property."""
        css_content = "body { position: absolute; }"
        errors = _validate_css_properties(tmp_path / "test.css", css_content)
        assert len(errors) == 1
        assert errors[0].id == "CSS-001"
        assert "position" in errors[0].message


# specmason: @scenario-EPUBCHECK-CSS-001-DIRECTION
class TestValidateCssDirection:
    """Test CSS direction validation."""

    def test_valid_direction_ltr(self, tmp_path: Path) -> None:
        """Test valid CSS direction ltr."""
        css_content = "body { direction: ltr; }"
        errors = _validate_css_direction(tmp_path / "test.css", css_content)
        assert len(errors) == 0

    def test_valid_direction_rtl(self, tmp_path: Path) -> None:
        """Test valid CSS direction rtl."""
        css_content = "body { direction: rtl; }"
        errors = _validate_css_direction(tmp_path / "test.css", css_content)
        assert len(errors) == 0

    def test_invalid_direction(self, tmp_path: Path) -> None:
        """Test invalid CSS direction."""
        css_content = "body { direction: invalid; }"
        errors = _validate_css_direction(tmp_path / "test.css", css_content)
        assert len(errors) == 1
        assert errors[0].id == "CSS-001"


# specmason: @scenario-EPUBCHECK-CSS-007
class TestValidateCssSelectors:
    """Test CSS selector validation."""

    def test_valid_selector(self, tmp_path: Path) -> None:
        """Test valid CSS selector."""
        css_content = "p { color: red; }"
        errors = _validate_css_selectors(tmp_path / "test.css", css_content)
        assert len(errors) == 0

    def test_pseudo_element(self, tmp_path: Path) -> None:
        """Test CSS pseudo-element."""
        css_content = "p::before { content: '→'; }"
        errors = _validate_css_selectors(tmp_path / "test.css", css_content)
        assert len(errors) == 0


# specmason: @scenario-EPUBCHECK-CSS-RUN
class TestRun:
    """Test run function."""

    def test_valid_css(self, tmp_path: Path) -> None:
        """Test valid CSS file."""
        css_file = tmp_path / "test.css"
        css_file.write_text("body { color: red; }")
        errors = run(css_file)
        assert len(errors) == 0

    def test_non_css_file(self, tmp_path: Path) -> None:
        """Test non-CSS file returns no errors."""
        xhtml_file = tmp_path / "test.xhtml"
        xhtml_file.write_text("<html/>")
        errors = run(xhtml_file)
        assert len(errors) == 0
