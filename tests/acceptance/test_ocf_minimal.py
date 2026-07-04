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


# Filename checker tests
from pyepubcheck.checks.ocf import check_filename


def test_filename_valid_ascii() -> None:
    """Valid ASCII filename should pass."""
    errors = check_filename("only-ascii")
    assert len(errors) == 0


def test_filename_valid_non_ascii() -> None:
    """Valid non-ASCII filename should pass."""
    errors = check_filename("not-ascii-é")
    assert len(errors) == 0


def test_filename_valid_ideograph() -> None:
    """Valid ideograph filename should pass."""
    errors = check_filename("ideograph-䀀")
    assert len(errors) == 0


def test_filename_valid_emoji() -> None:
    """Valid emoji filename should pass."""
    errors = check_filename("emoji-😊")
    assert len(errors) == 0


def test_filename_valid_emoji_tag_sequence() -> None:
    """Valid emoji tag sequence filename should pass."""
    errors = check_filename("emoji-tag-sequence-🏴󠁧󠁢󠁥󠁮󠁧󠁿")
    assert len(errors) == 0


def test_filename_space_warning() -> None:
    """Space character should report PKG-010 warning."""
    errors = check_filename("a name")
    assert any(e.id == "PKG-010" for e in errors)


def test_filename_tab_warning() -> None:
    """Tab character should report PKG-010 warning."""
    errors = check_filename("a\tname")
    assert any(e.id == "PKG-010" for e in errors)


def test_filename_full_stop_error() -> None:
    """Full stop as last character should report PKG-011 error."""
    errors = check_filename("aname.")
    assert any(e.id == "PKG-011" for e in errors)


def test_filename_forbidden_char() -> None:
    """Forbidden character should report PKG-009 error."""
    errors = check_filename("a*name")
    assert any(e.id == "PKG-009" for e in errors)
    assert any("U+002A" in e.message for e in errors)


def test_filename_multiple_forbidden_chars() -> None:
    """Multiple forbidden characters should be reported together."""
    errors = check_filename('a*na"me')
    assert any(e.id == "PKG-009" for e in errors)
    assert any("U+002A" in e.message and "U+0022" in e.message for e in errors)


def test_filename_repeated_forbidden_char() -> None:
    """Repeated forbidden character should be reported only once."""
    errors = check_filename("a*na*me")
    assert any(e.id == "PKG-009" for e in errors)
    # Should contain U+002A only once
    pkg009_errors = [e for e in errors if e.id == "PKG-009"]
    assert len(pkg009_errors) == 1


def test_filename_control_char_error() -> None:
    """Control character should report PKG-009 error."""
    errors = check_filename("a\x7fname")
    assert any(e.id == "PKG-009" for e in errors)
    assert any("CONTROL" in e.message for e in errors)
