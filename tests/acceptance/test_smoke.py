"""End-to-end smoke tests for pyepubcheck."""

from __future__ import annotations

import pytest

from pyepubcheck.api import validate_path


def test_validate_known_good_epub3(fixtures) -> None:
    """Validate a known-good EPUB 3 publication."""
    # Use the valid EPUB 3 fixture
    valid_epub = fixtures.fixture_path("/cli/files", "valid.epub")
    if not valid_epub.exists():
        pytest.skip("valid.epub fixture not found")
    
    report = validate_path(valid_epub)
    errors = [m for m in report.messages if m.severity.value in ("ERROR", "FATAL")]
    assert len(errors) == 0, f"Expected no errors, got: {[str(e) for e in errors]}"


def test_validate_known_bad_epub2(fixtures) -> None:
    """Validate a known-bad EPUB 2 publication."""
    # Use an EPUB 2 fixture that should have errors
    bad_epub = fixtures.fixture_path("/epub2/files", "epub/ocf-mimetype-missing-error")
    if not bad_epub.exists():
        pytest.skip("ocf-mimetype-missing-error fixture not found")
    
    report = validate_path(bad_epub)
    errors = [m for m in report.messages if m.severity.value in ("ERROR", "FATAL")]
    assert len(errors) > 0, "Expected at least one error for a known-bad EPUB"
