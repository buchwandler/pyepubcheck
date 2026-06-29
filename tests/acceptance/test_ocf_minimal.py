from __future__ import annotations

from pathlib import Path
from shutil import copytree


def _minimal_fixture(fixtures, name: str) -> Path:
    return fixtures.fixture_path("/epub3/00-minimal/files", name)


def _ocf_fixture(fixtures, name: str) -> Path:
    return fixtures.fixture_path("/epub3/04-ocf/files", name)


# specmason: @scenario-EPUBCHECK-3219CE85
def test_minimal_expanded_epub_passes(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck(
        _minimal_fixture(fixtures, "minimal"), transport="subprocess"
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-D895FA48
def test_minimal_packaged_epub_passes(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck(
        _minimal_fixture(fixtures, "minimal.epub"), transport="subprocess"
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: unmapped=test infrastructure for save/convert functionality
def test_save_creates_epub_from_expanded_directory(
    run_pyepubcheck, fixtures, tmp_path: Path
) -> None:
    source = _minimal_fixture(fixtures, "minimal")
    local_copy = tmp_path / "minimal"
    copytree(source, local_copy)
    result = run_pyepubcheck(
        "--mode", "exp", local_copy, "--save", transport="subprocess"
    )
    assert result.returncode == 0
    assert (tmp_path / "minimal.epub").is_file()


# specmason: @scenario-EPUBCHECK-E789B4C8
def test_missing_mimetype_reports_pkg_006(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck(
        _ocf_fixture(fixtures, "ocf-mimetype-file-missing-error"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("PKG-006")
    assert result.no_other_errors_or_warnings({"PKG-006"})


# specmason: @scenario-EPUBCHECK-58A778D2
def test_invalid_mimetype_reports_pkg_007(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck(
        _ocf_fixture(fixtures, "ocf-mimetype-file-incorrect-value-error"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("PKG-007")
    assert result.no_other_errors_or_warnings({"PKG-007"})
