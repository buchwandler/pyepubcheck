"""Acceptance tests for region navigation features.

Tests cover:
- epub-region-nav/region-nav-publication.feature (10 scenarios)
"""
from __future__ import annotations

from pathlib import Path

import pytest


def _region_nav_fixture(fixtures, name: str) -> Path:
    return fixtures.fixture_path("/epub-region-nav/files", name)


# specmason: @scenario-EPUBCHECK-30D84A43
@pytest.mark.xfail(reason="Region nav validation not yet implemented or fixture missing")
def test_region_nav_basic_valid(run_pyepubcheck, fixtures) -> None:
    """Verify a basic data nav file."""
    result = run_pyepubcheck(_region_nav_fixture(fixtures, "epub/data-nav-basic-valid"), transport="subprocess")
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-FFB6D1D2
def test_region_nav_not_xhtml(run_pyepubcheck, fixtures) -> None:
    """Report a data nav file that is not encoded as application/xhtml+xml."""
    result = run_pyepubcheck(_region_nav_fixture(fixtures, "epub/data-nav-not-xhtml-error"), transport="subprocess")
    assert result.returncode == 1
    assert result.has_error("OPF-012")


# specmason: @scenario-EPUBCHECK-D1EC67CE
@pytest.mark.xfail(reason="Region nav validation not yet implemented or fixture missing")
def test_region_nav_in_spine(run_pyepubcheck, fixtures) -> None:
    """Report a data nav file included in the spine."""
    result = run_pyepubcheck(_region_nav_fixture(fixtures, "epub/data-nav-in-spine-error"), transport="subprocess")
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-D4374D12
@pytest.mark.xfail(reason="Region nav validation not yet implemented or fixture missing")
def test_region_nav_unidentified_element(run_pyepubcheck, fixtures) -> None:
    """Report a data nav with an unidentified nav element in it."""
    result = run_pyepubcheck(_region_nav_fixture(fixtures, "epub/data-nav-unidentified-element-error"), transport="subprocess")
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-15EA5B7C
@pytest.mark.xfail(reason="Region nav validation not yet implemented or fixture missing")
def test_region_nav_multiple_files(run_pyepubcheck, fixtures) -> None:
    """Report the inclusion of more than one data nav file."""
    result = run_pyepubcheck(_region_nav_fixture(fixtures, "epub/data-nav-multiple-files-error"), transport="subprocess")
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-ACC24EA9
@pytest.mark.xfail(reason="Region nav validation not yet implemented or fixture missing")
def test_region_nav_valid(run_pyepubcheck, fixtures) -> None:
    """Verify a data nav that defines region-based navigation."""
    result = run_pyepubcheck(_region_nav_fixture(fixtures, "epub/region-nav-valid"), transport="subprocess")
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-49EF5922
@pytest.mark.xfail(reason="Region nav validation not yet implemented or fixture missing")
def test_region_nav_not_on_nav_element(run_pyepubcheck, fixtures) -> None:
    """Report region-based navigation not defined on a nav element."""
    result = run_pyepubcheck(_region_nav_fixture(fixtures, "epub/region-nav-not-on-nav-error"), transport="subprocess")
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-09EEB9F0
@pytest.mark.xfail(reason="Region nav validation not yet implemented or fixture missing")
def test_region_nav_not_fixed_layout(run_pyepubcheck, fixtures) -> None:
    """Report a region-based nav element that does not point to fixed-layout document."""
    result = run_pyepubcheck(_region_nav_fixture(fixtures, "epub/region-nav-not-fixed-layout-error"), transport="subprocess")
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-DF43DBCE
@pytest.mark.xfail(reason="Region nav validation not yet implemented or fixture missing")
def test_region_nav_invalid_content_model(run_pyepubcheck, fixtures) -> None:
    """Report a region-based nav element with an invalid content model."""
    result = run_pyepubcheck(_region_nav_fixture(fixtures, "epub/region-nav-content-model-error"), transport="subprocess")
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-B09E74A8
@pytest.mark.xfail(reason="Region nav validation not yet implemented or fixture missing")
def test_region_nav_comics_semantics(run_pyepubcheck, fixtures) -> None:
    """Verify subregion navigation using comics semantics."""
    result = run_pyepubcheck(_region_nav_fixture(fixtures, "epub/region-nav-comics-valid"), transport="subprocess")
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()
