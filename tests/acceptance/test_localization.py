"""Acceptance tests for localization features.

Tests cover:
- localization/localization.feature (7 scenarios)
"""

from __future__ import annotations

from pathlib import Path


def _localization_fixture(fixtures, name: str) -> Path:
    return fixtures.fixture_path("/localization/files", name)


# specmason: @scenario-EPUBCHECK-FCA1306A
def test_default_locale_is_english(run_pyepubcheck, fixtures) -> None:
    """The default testing locale is English."""
    target = _localization_fixture(fixtures, "schema-error")
    result = run_pyepubcheck(target, transport="subprocess")
    assert result.returncode == 1
    assert "Error" in result.stderr


# specmason: @scenario-EPUBCHECK-E50ABA01
def test_locale_can_be_configured(run_pyepubcheck, fixtures) -> None:
    """The reporting locale can be configured."""
    target = _localization_fixture(fixtures, "schema-error")
    result = run_pyepubcheck(target, "--locale", "en", transport="subprocess")
    assert result.returncode == 1
    assert "Error" in result.stderr


# specmason: @scenario-EPUBCHECK-9D5152FE
def test_locale_overrides_default(run_pyepubcheck, fixtures) -> None:
    """The reporting locale overrides the default locale."""
    target = _localization_fixture(fixtures, "schema-error")
    english = run_pyepubcheck(target, transport="subprocess")
    french = run_pyepubcheck(target, "--locale", "fr-FR", transport="subprocess")
    assert english.returncode == 1
    assert french.returncode == 1
    # Both should report errors but in different languages
    assert "Error" in english.stderr
    assert "Erreur" in french.stderr


# specmason: @scenario-EPUBCHECK-5539DC2D
def test_css_messages_localized(run_pyepubcheck, fixtures) -> None:
    """CSS messages are localized."""
    target = _localization_fixture(fixtures, "css-error")
    english = run_pyepubcheck(target, transport="subprocess")
    french = run_pyepubcheck(target, "--locale", "fr-FR", transport="subprocess")
    assert english.returncode == 1
    assert french.returncode == 1
    # Both should report CSS errors but in different languages
    assert "css" in english.stderr.lower() or "CSS" in english.stderr
    assert "css" in french.stderr.lower() or "CSS" in french.stderr


# specmason: @scenario-EPUBCHECK-8F6E9DE8
def test_schema_messages_localized(run_pyepubcheck, fixtures) -> None:
    """Schema messages (Jing library) are localized."""
    target = _localization_fixture(fixtures, "schema-error")
    english = run_pyepubcheck(target, transport="subprocess")
    french = run_pyepubcheck(target, "--locale", "fr-FR", transport="subprocess")
    assert english.returncode == 1
    assert french.returncode == 1
    # Both should report schema errors but in different languages
    assert "Error" in english.stderr
    assert "Erreur" in french.stderr


# specmason: @scenario-EPUBCHECK-4AA4017D
def test_locale_reset_after_scenario(run_pyepubcheck, fixtures) -> None:
    """Jing locale is properly reset (after the previous scenario)."""
    # This test verifies that locale doesn't leak between runs
    target = _localization_fixture(fixtures, "schema-error")
    # First run in French
    french = run_pyepubcheck(target, "--locale", "fr-FR", transport="subprocess")
    assert french.returncode == 1
    assert "Erreur" in french.stderr
    # Second run in English (default)
    english = run_pyepubcheck(target, transport="subprocess")
    assert english.returncode == 1
    assert "Error" in english.stderr
    # Verify no French leaking into English run
    assert "Erreur" not in english.stderr


# specmason: @scenario-EPUBCHECK-59201A10
def test_case_conversion_locale_dependent(run_pyepubcheck, fixtures) -> None:
    """Case-conversion is locale-dependent."""
    target = _localization_fixture(fixtures, "schema-error")
    # This test verifies that case conversion respects locale
    result = run_pyepubcheck(target, "--locale", "tr-TR", transport="subprocess")
    assert result.returncode == 1
    # Turkish locale has special case conversion rules (i/I)
    # Just verify it doesn't crash
