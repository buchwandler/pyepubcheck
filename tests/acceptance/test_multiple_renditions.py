"""Acceptance tests for multiple renditions features.

Tests cover:
- epub-multiple-renditions/multiple-rendition-publication.feature (13 scenarios)
"""

from __future__ import annotations

from pathlib import Path


def _multiple_renditions_fixture(fixtures, name: str) -> Path:
    return fixtures.fixture_path("/epub-multiple-renditions/files/epub", name)


# specmason: @scenario-EPUBCHECK-30D84A43
def test_multiple_renditions_basic(run_pyepubcheck, fixtures) -> None:
    """Verify a basic multiple rendition publication."""
    result = run_pyepubcheck(
        _multiple_renditions_fixture(fixtures, "renditions-basic-valid"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-FFB6D1D2
def test_multiple_renditions_container_required(run_pyepubcheck, fixtures) -> None:
    """Report a data nav file that is not encoded as application/xhtml+xml."""
    result = run_pyepubcheck(
        _multiple_renditions_fixture(fixtures, "renditions-mapping-non-xhtml-error"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-D1EC67CE
def test_multiple_renditions_spine_required(run_pyepubcheck, fixtures) -> None:
    """Report a data nav file included in the spine."""
    result = run_pyepubcheck(
        _multiple_renditions_fixture(
            fixtures, "renditions-mapping-no-resourcemap-error"
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-D4374D12
def test_multiple_renditions_nav_element(run_pyepubcheck, fixtures) -> None:
    """Report a data nav with an unidentified nav element in it."""
    result = run_pyepubcheck(
        _multiple_renditions_fixture(fixtures, "renditions-mapping-untyped-nav-error"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-15EA5B7C
def test_multiple_renditions_single_data_nav(run_pyepubcheck, fixtures) -> None:
    """Report the inclusion of more than one data nav file."""
    result = run_pyepubcheck(
        _multiple_renditions_fixture(
            fixtures, "renditions-mapping-multiple-docs-error"
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-ACC24EA9
def test_multiple_renditions_region_navigation(run_pyepubcheck, fixtures) -> None:
    """Verify a data nav that defines region-based navigation."""
    result = run_pyepubcheck(
        _multiple_renditions_fixture(fixtures, "renditions-mapping-multiple-nav-valid"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-49EF5922
def test_multiple_renditions_region_nav_element(run_pyepubcheck, fixtures) -> None:
    """Report region-based navigation not defined on a nav element."""
    result = run_pyepubcheck(
        _multiple_renditions_fixture(
            fixtures, "renditions-selection-attribute-unknown-error"
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-09EEB9F0
def test_multiple_renditions_region_nav_fixed_layout(run_pyepubcheck, fixtures) -> None:
    """Report a region-based nav element that does not point to fixed-layout document."""
    result = run_pyepubcheck(
        _multiple_renditions_fixture(
            fixtures, "renditions-selection-mediaquery-syntax-error"
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-DF43DBCE
def test_multiple_renditions_region_nav_content_model(
    run_pyepubcheck, fixtures
) -> None:
    """Report a region-based nav element with an invalid content model."""
    result = run_pyepubcheck(
        _multiple_renditions_fixture(
            fixtures, "renditions-selection-attribute-missing-error"
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.has_warning("RSC-017")


# specmason: @scenario-EPUBCHECK-B09E74A8
def test_multiple_renditions_comics_semantics(run_pyepubcheck, fixtures) -> None:
    """Verify subregion navigation using comics semantics."""
    result = run_pyepubcheck(
        _multiple_renditions_fixture(fixtures, "renditions-basic-valid"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-30D84A43
def test_multiple_renditions_metadata(run_pyepubcheck, fixtures) -> None:
    """Verify multiple renditions metadata."""
    result = run_pyepubcheck(
        _multiple_renditions_fixture(
            fixtures, "renditions-metadata-identifier-incomplete-error"
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-30D84A43
def test_multiple_renditions_rendition_mapping(run_pyepubcheck, fixtures) -> None:
    """Verify multiple renditions rendition mapping."""
    result = run_pyepubcheck(
        _multiple_renditions_fixture(fixtures, "renditions-mapping-multiple-nav-valid"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


def test_multiple_renditions_version(run_pyepubcheck, fixtures) -> None:
    """Verify multiple renditions version."""
    result = run_pyepubcheck(
        _multiple_renditions_fixture(fixtures, "renditions-mapping-no-version-error"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")
