"""Acceptance tests for multiple renditions features.

Tests cover:
- epub-multiple-renditions/multiple-rendition-publication.feature (13 scenarios)
"""
from __future__ import annotations

from pathlib import Path

import pytest


def _multiple_renditions_fixture(fixtures, name: str) -> Path:
    return fixtures.fixture_path("/epub-multiple-renditions/files", name)


# specmason: @scenario-EPUBCHECK-30D84A43
@pytest.mark.xfail(reason="Multiple renditions validation not yet implemented or fixture missing")
def test_multiple_renditions_basic(run_pyepubcheck, fixtures) -> None:
    """Verify a basic multiple rendition publication."""
    result = run_pyepubcheck(_multiple_renditions_fixture(fixtures, "epub/multiple-renditions-basic-valid"), transport="subprocess")
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-FFB6D1D2
@pytest.mark.xfail(reason="Multiple renditions validation not yet implemented or fixture missing")
def test_multiple_renditions_container_required(run_pyepubcheck, fixtures) -> None:
    """Report a data nav file that is not encoded as application/xhtml+xml."""
    result = run_pyepubcheck(_multiple_renditions_fixture(fixtures, "epub/multiple-renditions-container-error"), transport="subprocess")
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-D1EC67CE
@pytest.mark.xfail(reason="Multiple renditions validation not yet implemented or fixture missing")
def test_multiple_renditions_spine_required(run_pyepubcheck, fixtures) -> None:
    """Report a data nav file included in the spine."""
    result = run_pyepubcheck(_multiple_renditions_fixture(fixtures, "epub/multiple-renditions-spine-error"), transport="subprocess")
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-D4374D12
@pytest.mark.xfail(reason="Multiple renditions validation not yet implemented or fixture missing")
def test_multiple_renditions_nav_element(run_pyepubcheck, fixtures) -> None:
    """Report a data nav with an unidentified nav element in it."""
    result = run_pyepubcheck(_multiple_renditions_fixture(fixtures, "epub/multiple-renditions-nav-error"), transport="subprocess")
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-15EA5B7C
@pytest.mark.xfail(reason="Multiple renditions validation not yet implemented or fixture missing")
def test_multiple_renditions_single_data_nav(run_pyepubcheck, fixtures) -> None:
    """Report the inclusion of more than one data nav file."""
    result = run_pyepubcheck(_multiple_renditions_fixture(fixtures, "epub/multiple-renditions-multiple-nav-error"), transport="subprocess")
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-ACC24EA9
@pytest.mark.xfail(reason="Multiple renditions validation not yet implemented or fixture missing")
def test_multiple_renditions_region_navigation(run_pyepubcheck, fixtures) -> None:
    """Verify a data nav that defines region-based navigation."""
    result = run_pyepubcheck(_multiple_renditions_fixture(fixtures, "epub/multiple-renditions-region-nav-valid"), transport="subprocess")
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-49EF5922
@pytest.mark.xfail(reason="Multiple renditions validation not yet implemented or fixture missing")
def test_multiple_renditions_region_nav_element(run_pyepubcheck, fixtures) -> None:
    """Report region-based navigation not defined on a nav element."""
    result = run_pyepubcheck(_multiple_renditions_fixture(fixtures, "epub/multiple-renditions-region-nav-element-error"), transport="subprocess")
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-09EEB9F0
@pytest.mark.xfail(reason="Multiple renditions validation not yet implemented or fixture missing")
def test_multiple_renditions_region_nav_fixed_layout(run_pyepubcheck, fixtures) -> None:
    """Report a region-based nav element that does not point to fixed-layout document."""
    result = run_pyepubcheck(_multiple_renditions_fixture(fixtures, "epub/multiple-renditions-region-nav-fixed-layout-error"), transport="subprocess")
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-DF43DBCE
@pytest.mark.xfail(reason="Multiple renditions validation not yet implemented or fixture missing")
def test_multiple_renditions_region_nav_content_model(run_pyepubcheck, fixtures) -> None:
    """Report a region-based nav element with an invalid content model."""
    result = run_pyepubcheck(_multiple_renditions_fixture(fixtures, "epub/multiple-renditions-region-nav-content-model-error"), transport="subprocess")
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-B09E74A8
@pytest.mark.xfail(reason="Multiple renditions validation not yet implemented or fixture missing")
def test_multiple_renditions_comics_semantics(run_pyepubcheck, fixtures) -> None:
    """Verify subregion navigation using comics semantics."""
    result = run_pyepubcheck(_multiple_renditions_fixture(fixtures, "epub/multiple-renditions-comics-valid"), transport="subprocess")
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


@pytest.mark.xfail(reason="Multiple renditions validation not yet implemented")
# specmason: @scenario-EPUBCHECK-30D84A43
def test_multiple_renditions_metadata(run_pyepubcheck, fixtures) -> None:
    """Verify multiple renditions metadata."""
    result = run_pyepubcheck(_multiple_renditions_fixture(fixtures, "epub/multiple-renditions-metadata-valid"), transport="subprocess")
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


@pytest.mark.xfail(reason="Multiple renditions validation not yet implemented")
# specmason: @scenario-EPUBCHECK-30D84A43
def test_multiple_renditions_rendition_mapping(run_pyepubcheck, fixtures) -> None:
    """Verify multiple renditions rendition mapping."""
    result = run_pyepubcheck(_multiple_renditions_fixture(fixtures, "epub/multiple-renditions-rendition-mapping-valid"), transport="subprocess")
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


@pytest.mark.xfail(reason="Multiple renditions validation not yet implemented")
# specmason: @scenario-EPUBCHECK-30D84A43
def test_multiple_renditions_version(run_pyepubcheck, fixtures) -> None:
    """Verify multiple renditions version."""
    result = run_pyepubcheck(_multiple_renditions_fixture(fixtures, "epub/multiple-renditions-version-valid"), transport="subprocess")
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()
