"""End-to-end smoke tests for pyepubcheck."""

from __future__ import annotations

import pytest

from pyepubcheck.api import validate_path


def test_validate_known_good_epub3(fixtures) -> None:
    """Validate a known-good EPUB 3 publication."""
    valid_epub = fixtures.fixture_path("/cli/files", "valid.epub")
    if not valid_epub.exists():
        pytest.skip("valid.epub fixture not found")

    report = validate_path(valid_epub)
    errors = [m for m in report.messages if m.severity.value in ("ERROR", "FATAL")]
    assert len(errors) == 0, f"Expected no errors, got: {[str(e) for e in errors]}"


def test_validate_known_bad_epub2(fixtures) -> None:
    """Validate a known-bad EPUB 2 publication."""
    bad_epub = fixtures.fixture_path("/epub2/files", "epub/ocf-mimetype-missing-error")
    if not bad_epub.exists():
        pytest.skip("ocf-mimetype-missing-error fixture not found")

    report = validate_path(bad_epub)
    errors = [m for m in report.messages if m.severity.value in ("ERROR", "FATAL")]
    assert len(errors) > 0, "Expected at least one error for a known-bad EPUB"


def test_validate_usage_reporting(fixtures) -> None:
    """Smoke test for OPF-003 USAGE on a container resource not in the manifest."""
    fixture = fixtures.fixture_path(
        "/epub2/files", "epub/opf-manifest-resource-undeclared-usage"
    )
    if not fixture.exists():
        pytest.skip("opf-manifest-resource-undeclared-usage fixture not found")

    report = validate_path(fixture)
    usage_messages = [m for m in report.messages if m.severity.value == "USAGE"]
    assert any(m.id == "OPF-003" for m in usage_messages), (
        "Expected an OPF-003 USAGE message for a container file not in the manifest."
    )


def test_validate_hyperlinked_document_spine(fixtures) -> None:
    """Smoke test for RSC-011 on a hyperlink to a missing fragment."""
    fixture = fixtures.fixture_path(
        "/epub2/files", "epub/ops-xhtml-hyperlink-to-missing-fragment-error"
    )
    if not fixture.exists():
        pytest.skip("ops-xhtml-hyperlink-to-missing-fragment-error fixture not found")

    report = validate_path(fixture)
    errors = [m for m in report.messages if m.severity.value in ("ERROR", "FATAL")]
    assert any(m.id == "RSC-011" for m in errors), (
        "Expected an RSC-011 ERROR for a hyperlink to a missing fragment."
    )


def test_validate_html5_doctype_in_epub2(fixtures) -> None:
    """Smoke test for HTML5 DOCTYPE detection in an EPUB 2 single XHTML file."""
    fixture = fixtures.fixture_path(
        "/epub2/files", "ops-document-xhtml/doctype-html5-error.xhtml"
    )
    if not fixture.exists():
        pytest.skip("doctype-html5-error.xhtml fixture not found")

    report = validate_path(fixture)
    errors = [m for m in report.messages if m.severity.value in ("ERROR", "FATAL")]
    assert any(m.id == "RSC-005" for m in errors), (
        "Expected an RSC-005 ERROR for an HTML5 DOCTYPE in EPUB 2."
    )


def test_validate_profile_tagged_publication(fixtures) -> None:
    """Smoke test for a profile-tagged publication (dict profile)."""
    fixture = fixtures.fixture_path(
        "/epub-dictionaries/files", "epub/dictionary-single-valid"
    )
    if not fixture.exists():
        pytest.skip("dictionary-single-valid fixture not found")

    report = validate_path(fixture)
    fatal = [m for m in report.messages if m.severity.value in ("ERROR", "FATAL")]
    assert len(fatal) == 0, (
        f"Expected no fatal errors for a valid dictionary publication, "
        f"got: {[str(e) for e in fatal]}"
    )
