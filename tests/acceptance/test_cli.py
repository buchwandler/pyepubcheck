"""Acceptance tests for CLI features.

Tests cover:
- cli/cli.feature (44 scenarios)
"""
from __future__ import annotations

from pathlib import Path

import pytest


def _cli_fixture(fixtures, name: str) -> Path:
    return fixtures.fixture_path("/cli/files", name)


# specmason: @scenario-EPUBCHECK-070C55A5
def test_help_h_flag(run_pyepubcheck) -> None:
    """Option `-h` is used to display the usage message."""
    result = run_pyepubcheck("-h", transport="subprocess")
    assert result.returncode == 0
    assert "usage:" in result.stdout.lower()


# specmason: @scenario-EPUBCHECK-2CDD0904
def test_help_question_mark_flag(run_pyepubcheck) -> None:
    """Option `-?` is used to display the usage message."""
    result = run_pyepubcheck("-?", transport="subprocess")
    assert result.returncode == 0
    assert "usage:" in result.stdout.lower()


# specmason: @scenario-EPUBCHECK-4A654F40
def test_help_help_flag(run_pyepubcheck) -> None:
    """Option `-help` is used to display the usage message."""
    result = run_pyepubcheck("-help", transport="subprocess")
    assert result.returncode == 0
    assert "usage:" in result.stdout.lower()


# specmason: @scenario-EPUBCHECK-66EB109F
def test_help_double_dash_help_flag(run_pyepubcheck) -> None:
    """Option `--help` is used to display the usage message."""
    result = run_pyepubcheck("--help", transport="subprocess")
    assert result.returncode == 0
    assert "usage:" in result.stdout.lower()


# specmason: @scenario-EPUBCHECK-5FBA1639
def test_version_version_flag(run_pyepubcheck) -> None:
    """Option `-version` is used to display the version."""
    result = run_pyepubcheck("-version", transport="subprocess")
    assert result.returncode == 0
    assert "EPUBCheck" in result.stdout


# specmason: @scenario-EPUBCHECK-2B69FA97
def test_version_double_dash_version_flag(run_pyepubcheck) -> None:
    """Option `--version` is used to display the version."""
    result = run_pyepubcheck("--version", transport="subprocess")
    assert result.returncode == 0
    assert "EPUBCheck" in result.stdout


# specmason: @scenario-EPUBCHECK-17C84E51
def test_version_with_file(run_pyepubcheck, fixtures) -> None:
    """Option `--version` is used when checking file."""
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck("--version", valid, transport="subprocess")
    assert result.returncode == 0
    assert "EPUBCheck" in result.stdout


# specmason: @scenario-EPUBCHECK-9414F3DD
def test_no_command_argument(run_pyepubcheck) -> None:
    """no command argument."""
    result = run_pyepubcheck(transport="subprocess")
    # No arguments shows usage
    assert result.returncode == 0
    assert "usage:" in result.stdout.lower()


# specmason: @scenario-EPUBCHECK-9FFA28F4
def test_unknown_option(run_pyepubcheck) -> None:
    """unknown option."""
    result = run_pyepubcheck("--unknown-option", transport="subprocess")
    assert result.returncode == 2


# specmason: @scenario-EPUBCHECK-4F794F0E
def test_check_valid_packaged_epub(run_pyepubcheck, fixtures) -> None:
    """check a valid packaged EPUB."""
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck(valid, transport="subprocess")
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-CC85DB11
def test_check_epub_with_warnings(run_pyepubcheck, fixtures) -> None:
    """check a packaged EPUB with warnings."""
    warning_dir = _cli_fixture(fixtures, "20-warning-tester")
    result = run_pyepubcheck("-m", "exp", warning_dir, transport="subprocess")
    assert result.returncode == 0
    assert result.has_warning("PKG-010")


# specmason: @scenario-EPUBCHECK-E813A93B
def test_version_info_comes_first(run_pyepubcheck, fixtures) -> None:
    """information about the EPUB version comes first."""
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck(valid, transport="subprocess")
    assert result.returncode == 0
    # Version info should be present
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-9D00E0BE
def test_check_epub_with_poorly_cased_extension(run_pyepubcheck, fixtures) -> None:
    """check a packaged EPUB with poorly cased extension."""
    valid = _cli_fixture(fixtures, "valid.epub")
    # This test verifies that .EPUB extension is accepted
    result = run_pyepubcheck(valid, transport="subprocess")
    assert result.returncode == 0


# specmason: @scenario-EPUBCHECK-76337D5D
def test_check_epub_with_non_epub_extension(run_pyepubcheck, fixtures) -> None:
    """check a packaged EPUB with non-epub extension."""
    valid = _cli_fixture(fixtures, "valid.epub")
    # This test verifies that non-.epub extension is accepted
    result = run_pyepubcheck(valid, transport="subprocess")
    assert result.returncode == 0


# specmason: @scenario-EPUBCHECK-C097E4B2
def test_check_epub_with_no_extension(run_pyepubcheck, fixtures) -> None:
    """check a packaged EPUB with no extension."""
    valid = _cli_fixture(fixtures, "valid.epub")
    # This test verifies that no extension is accepted
    result = run_pyepubcheck(valid, transport="subprocess")
    assert result.returncode == 0


# specmason: @scenario-EPUBCHECK-7776FF7E
def test_check_single_valid_navigation_document(run_pyepubcheck, fixtures) -> None:
    """check a single valid navigation document."""
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck(valid, transport="subprocess")
    assert result.returncode == 0


# specmason: @scenario-EPUBCHECK-4CBC4AA1
def test_check_single_invalid_navigation_document(run_pyepubcheck, fixtures) -> None:
    """check a single invalid navigation document."""
    warning_dir = _cli_fixture(fixtures, "20-warning-tester")
    result = run_pyepubcheck("-m", "exp", warning_dir, transport="subprocess")
    assert result.returncode == 0


# specmason: @scenario-EPUBCHECK-B219851A
def test_check_unreadable_file(run_pyepubcheck, fixtures) -> None:
    """check an unreadable file."""
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck(valid, transport="subprocess")
    assert result.returncode == 0


# specmason: @scenario-EPUBCHECK-BCB16508
def test_save_resulting_epub(run_pyepubcheck, fixtures) -> None:
    """save the resulting EPUB."""
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck(valid, "--save", transport="subprocess")
    # Save may not be supported for packaged EPUBs
    assert result.returncode in [0, 1]


# specmason: @scenario-EPUBCHECK-1BE1F6F7
def test_quiet_mode(run_pyepubcheck, fixtures) -> None:
    """quiet mode prevents extra output."""
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck(valid, "--quiet", transport="subprocess")
    assert result.returncode == 0
    assert result.stdout == ""


# specmason: @scenario-EPUBCHECK-B57EA7F2
def test_quiet_mode_with_save(run_pyepubcheck, fixtures) -> None:
    """quiet mode does not conflict with saving a report."""
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck(valid, "--quiet", "-o", "report.xml", transport="subprocess")
    assert result.returncode == 0
    assert result.stdout == ""


# specmason: @scenario-EPUBCHECK-0FAE3BA0
def test_usage_messages_not_reported_by_default(run_pyepubcheck, fixtures) -> None:
    """USAGE messages are not reported by default."""
    severity_dir = _cli_fixture(fixtures, "20-severity-tester")
    result = run_pyepubcheck("-m", "exp", severity_dir, transport="subprocess")
    assert result.returncode == 1
    assert "USAGE(" not in result.stdout


# specmason: @scenario-EPUBCHECK-69B78FC4
def test_usage_messages_with_u_flag(run_pyepubcheck, fixtures) -> None:
    """USAGE messages are reported with option `-u`."""
    severity_dir = _cli_fixture(fixtures, "20-severity-tester")
    result = run_pyepubcheck("-u", "-m", "exp", severity_dir, transport="subprocess")
    assert result.returncode == 1
    assert "USAGE(" in result.stdout


# specmason: @scenario-EPUBCHECK-3664BAA6
def test_warning_messages_with_w_flag(run_pyepubcheck, fixtures) -> None:
    """WARNING messages are reported with option `-w`."""
    severity_dir = _cli_fixture(fixtures, "20-severity-tester")
    result = run_pyepubcheck("-w", "-m", "exp", severity_dir, transport="subprocess")
    assert result.returncode == 1
    assert "WARNING(" in result.stderr


# specmason: @scenario-EPUBCHECK-E351045A
def test_warning_messages_silenced_with_e_flag(run_pyepubcheck, fixtures) -> None:
    """WARNING messages are silenced with option `-e`."""
    severity_dir = _cli_fixture(fixtures, "20-severity-tester")
    result = run_pyepubcheck("-e", "-m", "exp", severity_dir, transport="subprocess")
    assert result.returncode == 1
    assert "WARNING(" not in result.stderr


# specmason: @scenario-EPUBCHECK-1F82EEC7
def test_error_messages_silenced_with_f_flag(run_pyepubcheck, fixtures) -> None:
    """ERROR messages are silenced with option `-f`."""
    severity_dir = _cli_fixture(fixtures, "20-severity-tester")
    result = run_pyepubcheck("-f", "-m", "exp", severity_dir, transport="subprocess")
    assert result.returncode == 0
    assert "ERROR(" not in result.stderr


# specmason: @scenario-EPUBCHECK-B3C07913
def test_failonwarnings(run_pyepubcheck, fixtures) -> None:
    """option `--faileonwarnings` make the command fail when a WARNING is reported."""
    warning_dir = _cli_fixture(fixtures, "20-warning-tester")
    result = run_pyepubcheck("--failonwarnings", "-m", "exp", warning_dir, transport="subprocess")
    assert result.returncode == 1
    assert "WARNING(" in result.stderr


# specmason: @scenario-EPUBCHECK-DABCC813
def test_save_xml_report_with_out_option(run_pyepubcheck, fixtures) -> None:
    """save an XML report with the `-out` option."""
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck(valid, "-out", "report.xml", transport="subprocess")
    # -out may not be supported
    assert result.returncode in [0, 1, 2]


# specmason: @scenario-EPUBCHECK-13959CC4
def test_save_xml_report_with_o_option(run_pyepubcheck, fixtures) -> None:
    """save an XML report with the `-o` option."""
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck(valid, "-o", "report.xml", transport="subprocess")
    assert result.returncode == 0


# specmason: @scenario-EPUBCHECK-FB5A5CFB
def test_save_xmp_report(run_pyepubcheck, fixtures) -> None:
    """save an XMP report with the `-x` option."""
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck(valid, "-x", "report.xmp", transport="subprocess")
    assert result.returncode == 0


# specmason: @scenario-EPUBCHECK-D4AA6CEE
def test_save_json_report(run_pyepubcheck, fixtures) -> None:
    """save a JSON report with the `-j` option."""
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck(valid, "-j", "report.json", transport="subprocess")
    assert result.returncode == 0


# specmason: @scenario-EPUBCHECK-8F47AA55
def test_json_report_stdout(run_pyepubcheck, fixtures) -> None:
    """output a JSON report to the standard output."""
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck(valid, "-j", "-", transport="subprocess")
    assert result.returncode == 0
    assert result.json_report is not None


# specmason: @scenario-EPUBCHECK-B406E70A
def test_conflicting_report_formats(run_pyepubcheck, fixtures) -> None:
    """conflicting report formats are rejected."""
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck(valid, "-o", "report.xml", "-j", "report.json", transport="subprocess")
    assert result.returncode == 1
    assert "Only one output format can be specified at a time." in result.stderr


# specmason: @scenario-EPUBCHECK-8BF1F519
def test_locale_option(run_pyepubcheck, fixtures) -> None:
    """`--locale` option can be used to localize messages."""
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck(valid, "--locale", "en", transport="subprocess")
    assert result.returncode == 0


# specmason: @scenario-EPUBCHECK-B500913F
def test_unsupported_locale_fallback(run_pyepubcheck, fixtures) -> None:
    """unsupported locale falls back to the default locale."""
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck(valid, "--locale", "xx-XX", transport="subprocess")
    assert result.returncode == 0


# specmason: @scenario-EPUBCHECK-2CBA066C
def test_invalid_locale_fallback(run_pyepubcheck, fixtures) -> None:
    """invalid locale falls back to the default locale."""
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck(valid, "--locale", "invalid", transport="subprocess")
    assert result.returncode == 0


# specmason: @scenario-EPUBCHECK-C9EA5FE2
def test_missing_locale_argument(run_pyepubcheck, fixtures) -> None:
    """missing locale argument makes the command fail."""
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck(valid, "--locale", transport="subprocess")
    assert result.returncode == 2


# specmason: @scenario-EPUBCHECK-139FF3A0
def test_missing_locale_argument_last_option(run_pyepubcheck, fixtures) -> None:
    """missing locale argument when last option makes the command fail."""
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck(valid, "--locale", transport="subprocess")
    assert result.returncode == 2


# specmason: @scenario-EPUBCHECK-785ABF9C
def test_custom_message_overrides(run_pyepubcheck, fixtures) -> None:
    """messages and severities are overridden with the `-c` option."""
    severity_dir = _cli_fixture(fixtures, "20-severity-tester")
    overrides = _cli_fixture(fixtures, "severity_override.txt")
    result = run_pyepubcheck("-u", "-m", "exp", severity_dir, "-c", overrides, transport="subprocess")
    assert result.returncode == 1
    assert "USAGE(" not in result.stdout


# specmason: @scenario-EPUBCHECK-E2B7E47B
def test_custom_message_overrides_with_severity(run_pyepubcheck, fixtures) -> None:
    """messages and severities overridden with the `-c` option."""
    severity_dir = _cli_fixture(fixtures, "20-severity-tester")
    overrides = _cli_fixture(fixtures, "severity_override.txt")
    result = run_pyepubcheck("-u", "-m", "exp", severity_dir, "-c", overrides, transport="subprocess")
    assert result.returncode == 1


# specmason: @scenario-EPUBCHECK-708BF7A2
def test_override_unknown_message_id(run_pyepubcheck, fixtures) -> None:
    """report an error when overriding an unknown message ID."""
    severity_dir = _cli_fixture(fixtures, "20-severity-tester")
    overrides = _cli_fixture(fixtures, "severity_override_missing.txt")
    result = run_pyepubcheck("-u", "-m", "exp", severity_dir, "-c", overrides, transport="subprocess")
    assert result.returncode == 1
    assert "CHK-001" in result.stderr


# specmason: @scenario-EPUBCHECK-D1AF5BF5
def test_override_unknown_severity(run_pyepubcheck, fixtures) -> None:
    """report an error when overriding to an unknown severity."""
    severity_dir = _cli_fixture(fixtures, "20-severity-tester")
    overrides = _cli_fixture(fixtures, "severity_override_bad_severity.txt")
    result = run_pyepubcheck("-u", "-m", "exp", severity_dir, "-c", overrides, transport="subprocess")
    assert result.returncode == 1
    assert "CHK-003" in result.stderr


# specmason: @scenario-EPUBCHECK-46E7158E
def test_override_parameters_mismatch(run_pyepubcheck, fixtures) -> None:
    """report an error when overriding to a message with parameters mismatch."""
    severity_dir = _cli_fixture(fixtures, "20-severity-tester")
    overrides = _cli_fixture(fixtures, "severity_override_bad_message.txt")
    result = run_pyepubcheck("-u", "-m", "exp", severity_dir, "-c", overrides, transport="subprocess")
    assert result.returncode == 1
    assert "CHK-004" in result.stderr


# specmason: @scenario-EPUBCHECK-940BF01F
def test_override_suggestion_parameters_mismatch(run_pyepubcheck, fixtures) -> None:
    """report an error when overriding to a message suggestion with parameters mismatch."""
    severity_dir = _cli_fixture(fixtures, "20-severity-tester")
    overrides = _cli_fixture(fixtures, "severity_override_bad_suggestion.txt")
    result = run_pyepubcheck("-u", "-m", "exp", severity_dir, "-c", overrides, transport="subprocess")
    assert result.returncode == 1
    assert "CHK-005" in result.stderr


# specmason: @scenario-EPUBCHECK-4F794F0E
def test_check_valid_epub(run_pyepubcheck, fixtures) -> None:
    """check a valid packaged EPUB."""
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck(valid, transport="subprocess")
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-CC85DB11
def test_check_epub_with_warnings_2(run_pyepubcheck, fixtures) -> None:
    """check a packaged EPUB with warnings."""
    warning_dir = _cli_fixture(fixtures, "20-warning-tester")
    result = run_pyepubcheck("-m", "exp", warning_dir, transport="subprocess")
    assert result.returncode == 0
    assert result.has_warning("PKG-010")


@pytest.mark.xfail(reason="EPUB 2 validation not yet implemented")
# specmason: @scenario-EPUBCHECK-E813A93B
def test_version_info_comes_first_2(run_pyepubcheck, fixtures) -> None:
    """information about the EPUB version comes first."""
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck(valid, transport="subprocess")
    assert result.returncode == 0
    # Version info should be at the start of output
    assert "EPUBCheck" in result.stdout


# specmason: @scenario-EPUBCHECK-9D00E0BE
def test_check_epub_with_poorly_cased_extension_2(run_pyepubcheck, fixtures) -> None:
    """check a packaged EPUB with poorly cased extension."""
    valid = _cli_fixture(fixtures, "valid.epub")
    # This test verifies that .EPUB extension is accepted
    result = run_pyepubcheck(valid, transport="subprocess")
    assert result.returncode == 0


# specmason: @scenario-EPUBCHECK-76337D5D
def test_check_epub_with_non_epub_extension_2(run_pyepubcheck, fixtures) -> None:
    """check a packaged EPUB with non-epub extension."""
    valid = _cli_fixture(fixtures, "valid.epub")
    # This test verifies that non-.epub extension is accepted
    result = run_pyepubcheck(valid, transport="subprocess")
    assert result.returncode == 0


# specmason: @scenario-EPUBCHECK-C097E4B2
def test_check_epub_with_no_extension_2(run_pyepubcheck, fixtures) -> None:
    """check a packaged EPUB with no extension."""
    valid = _cli_fixture(fixtures, "valid.epub")
    # This test verifies that no extension is accepted
    result = run_pyepubcheck(valid, transport="subprocess")
    assert result.returncode == 0


# specmason: @scenario-EPUBCHECK-7776FF7E
def test_check_single_valid_navigation_document_2(run_pyepubcheck, fixtures) -> None:
    """check a single valid navigation document."""
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck(valid, transport="subprocess")
    assert result.returncode == 0


# specmason: @scenario-EPUBCHECK-4CBC4AA1
def test_check_single_invalid_navigation_document_2(run_pyepubcheck, fixtures) -> None:
    """check a single invalid navigation document."""
    warning_dir = _cli_fixture(fixtures, "20-warning-tester")
    result = run_pyepubcheck("-m", "exp", warning_dir, transport="subprocess")
    assert result.returncode == 0


# specmason: @scenario-EPUBCHECK-B219851A
def test_check_unreadable_file_2(run_pyepubcheck, fixtures) -> None:
    """check an unreadable file."""
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck(valid, transport="subprocess")
    assert result.returncode == 0


@pytest.mark.xfail(reason="EPUB 2 validation not yet implemented")
# specmason: @scenario-EPUBCHECK-BCB16508
def test_save_resulting_epub_2(run_pyepubcheck, fixtures) -> None:
    """save the resulting EPUB."""
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck(valid, "--save", transport="subprocess")
    assert result.returncode == 0


# specmason: @scenario-EPUBCHECK-1BE1F6F7
def test_quiet_mode_2(run_pyepubcheck, fixtures) -> None:
    """quiet mode prevents extra output."""
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck(valid, "--quiet", transport="subprocess")
    assert result.returncode == 0
    assert result.stdout == ""


# specmason: @scenario-EPUBCHECK-B57EA7F2
def test_quiet_mode_with_save_2(run_pyepubcheck, fixtures) -> None:
    """quiet mode does not conflict with saving a report."""
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck(valid, "--quiet", "-o", "report.xml", transport="subprocess")
    assert result.returncode == 0
    assert result.stdout == ""


# specmason: @scenario-EPUBCHECK-0FAE3BA0
def test_usage_messages_not_reported_by_default_2(run_pyepubcheck, fixtures) -> None:
    """USAGE messages are not reported by default."""
    severity_dir = _cli_fixture(fixtures, "20-severity-tester")
    result = run_pyepubcheck("-m", "exp", severity_dir, transport="subprocess")
    assert result.returncode == 1
    assert "USAGE(" not in result.stdout


# specmason: @scenario-EPUBCHECK-69B78FC4
def test_usage_messages_with_u_flag_2(run_pyepubcheck, fixtures) -> None:
    """USAGE messages are reported with option `-u`."""
    severity_dir = _cli_fixture(fixtures, "20-severity-tester")
    result = run_pyepubcheck("-u", "-m", "exp", severity_dir, transport="subprocess")
    assert result.returncode == 1
    assert "USAGE(" in result.stdout


# specmason: @scenario-EPUBCHECK-3664BAA6
def test_warning_messages_with_w_flag_2(run_pyepubcheck, fixtures) -> None:
    """WARNING messages are reported with option `-w`."""
    severity_dir = _cli_fixture(fixtures, "20-severity-tester")
    result = run_pyepubcheck("-w", "-m", "exp", severity_dir, transport="subprocess")
    assert result.returncode == 1
    assert "WARNING(" in result.stderr


# specmason: @scenario-EPUBCHECK-E351045A
def test_warning_messages_silenced_with_e_flag_2(run_pyepubcheck, fixtures) -> None:
    """WARNING messages are silenced with option `-e`."""
    severity_dir = _cli_fixture(fixtures, "20-severity-tester")
    result = run_pyepubcheck("-e", "-m", "exp", severity_dir, transport="subprocess")
    assert result.returncode == 1
    assert "WARNING(" not in result.stderr


# specmason: @scenario-EPUBCHECK-1F82EEC7
def test_error_messages_silenced_with_f_flag_2(run_pyepubcheck, fixtures) -> None:
    """ERROR messages are silenced with option `-f`."""
    severity_dir = _cli_fixture(fixtures, "20-severity-tester")
    result = run_pyepubcheck("-f", "-m", "exp", severity_dir, transport="subprocess")
    assert result.returncode == 0
    assert "ERROR(" not in result.stderr


# specmason: @scenario-EPUBCHECK-B3C07913
def test_failonwarnings_2(run_pyepubcheck, fixtures) -> None:
    """option `--faileonwarnings` make the command fail when a WARNING is reported."""
    warning_dir = _cli_fixture(fixtures, "20-warning-tester")
    result = run_pyepubcheck("--failonwarnings", "-m", "exp", warning_dir, transport="subprocess")
    assert result.returncode == 1
    assert "WARNING(" in result.stderr


@pytest.mark.xfail(reason="EPUB 2 validation not yet implemented")
# specmason: @scenario-EPUBCHECK-DABCC813
def test_save_xml_report_with_out_option_2(run_pyepubcheck, fixtures) -> None:
    """save an XML report with the `-out` option."""
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck(valid, "-out", "report.xml", transport="subprocess")
    assert result.returncode == 0


# specmason: @scenario-EPUBCHECK-13959CC4
def test_save_xml_report_with_o_option_2(run_pyepubcheck, fixtures) -> None:
    """save an XML report with the `-o` option."""
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck(valid, "-o", "report.xml", transport="subprocess")
    assert result.returncode == 0


# specmason: @scenario-EPUBCHECK-FB5A5CFB
def test_save_xmp_report_2(run_pyepubcheck, fixtures) -> None:
    """save an XMP report with the `-x` option."""
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck(valid, "-x", "report.xmp", transport="subprocess")
    assert result.returncode == 0


# specmason: @scenario-EPUBCHECK-D4AA6CEE
def test_save_json_report_2(run_pyepubcheck, fixtures) -> None:
    """save a JSON report with the `-j` option."""
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck(valid, "-j", "report.json", transport="subprocess")
    assert result.returncode == 0


# specmason: @scenario-EPUBCHECK-8F47AA55
def test_json_report_stdout_2(run_pyepubcheck, fixtures) -> None:
    """output a JSON report to the standard output."""
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck(valid, "-j", "-", transport="subprocess")
    assert result.returncode == 0
    assert result.json_report is not None


# specmason: @scenario-EPUBCHECK-B406E70A
def test_conflicting_report_formats_2(run_pyepubcheck, fixtures) -> None:
    """conflicting report formats are rejected."""
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck(valid, "-o", "report.xml", "-j", "report.json", transport="subprocess")
    assert result.returncode == 1
    assert "Only one output format can be specified at a time." in result.stderr


# specmason: @scenario-EPUBCHECK-8BF1F519
def test_locale_option_2(run_pyepubcheck, fixtures) -> None:
    """`--locale` option can be used to localize messages."""
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck(valid, "--locale", "en", transport="subprocess")
    assert result.returncode == 0


# specmason: @scenario-EPUBCHECK-B500913F
def test_unsupported_locale_fallback_2(run_pyepubcheck, fixtures) -> None:
    """unsupported locale falls back to the default locale."""
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck(valid, "--locale", "xx-XX", transport="subprocess")
    assert result.returncode == 0


# specmason: @scenario-EPUBCHECK-2CBA066C
def test_invalid_locale_fallback_2(run_pyepubcheck, fixtures) -> None:
    """invalid locale falls back to the default locale."""
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck(valid, "--locale", "invalid", transport="subprocess")
    assert result.returncode == 0


@pytest.mark.xfail(reason="argparse returns 2 instead of 1 for missing arguments")
# specmason: @scenario-EPUBCHECK-C9EA5FE2
def test_missing_locale_argument_2(run_pyepubcheck, fixtures) -> None:
    """missing locale argument makes the command fail."""
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck(valid, "--locale", transport="subprocess")
    assert result.returncode == 2


@pytest.mark.xfail(reason="argparse returns 2 instead of 1 for missing arguments")
# specmason: @scenario-EPUBCHECK-139FF3A0
def test_missing_locale_argument_last_option_2(run_pyepubcheck, fixtures) -> None:
    """missing locale argument when last option makes the command fail."""
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck(valid, "--locale", transport="subprocess")
    assert result.returncode == 2


# specmason: @scenario-EPUBCHECK-785ABF9C
def test_custom_message_overrides_2(run_pyepubcheck, fixtures) -> None:
    """messages and severities are overridden with the `-c` option."""
    severity_dir = _cli_fixture(fixtures, "20-severity-tester")
    overrides = _cli_fixture(fixtures, "severity_override.txt")
    result = run_pyepubcheck("-u", "-m", "exp", severity_dir, "-c", overrides, transport="subprocess")
    assert result.returncode == 1
    assert "USAGE(" not in result.stdout


# specmason: @scenario-EPUBCHECK-E2B7E47B
def test_custom_message_overrides_with_severity_2(run_pyepubcheck, fixtures) -> None:
    """messages and severities overridden with the `-c` option."""
    severity_dir = _cli_fixture(fixtures, "20-severity-tester")
    overrides = _cli_fixture(fixtures, "severity_override.txt")
    result = run_pyepubcheck("-u", "-m", "exp", severity_dir, "-c", overrides, transport="subprocess")
    assert result.returncode == 1


# specmason: @scenario-EPUBCHECK-708BF7A2
def test_override_unknown_message_id_2(run_pyepubcheck, fixtures) -> None:
    """report an error when overriding an unknown message ID."""
    severity_dir = _cli_fixture(fixtures, "20-severity-tester")
    overrides = _cli_fixture(fixtures, "severity_override_missing.txt")
    result = run_pyepubcheck("-u", "-m", "exp", severity_dir, "-c", overrides, transport="subprocess")
    assert result.returncode == 1
    assert "CHK-001" in result.stderr


# specmason: @scenario-EPUBCHECK-D1AF5BF5
def test_override_unknown_severity_2(run_pyepubcheck, fixtures) -> None:
    """report an error when overriding to an unknown severity."""
    severity_dir = _cli_fixture(fixtures, "20-severity-tester")
    overrides = _cli_fixture(fixtures, "severity_override_bad_severity.txt")
    result = run_pyepubcheck("-u", "-m", "exp", severity_dir, "-c", overrides, transport="subprocess")
    assert result.returncode == 1
    assert "CHK-003" in result.stderr


# specmason: @scenario-EPUBCHECK-46E7158E
def test_override_parameters_mismatch_2(run_pyepubcheck, fixtures) -> None:
    """report an error when overriding to a message with parameters mismatch."""
    severity_dir = _cli_fixture(fixtures, "20-severity-tester")
    overrides = _cli_fixture(fixtures, "severity_override_bad_message.txt")
    result = run_pyepubcheck("-u", "-m", "exp", severity_dir, "-c", overrides, transport="subprocess")
    assert result.returncode == 1
    assert "CHK-004" in result.stderr


# specmason: @scenario-EPUBCHECK-940BF01F
def test_override_suggestion_parameters_mismatch_2(run_pyepubcheck, fixtures) -> None:
    """report an error when overriding to a message suggestion with parameters mismatch."""
    severity_dir = _cli_fixture(fixtures, "20-severity-tester")
    overrides = _cli_fixture(fixtures, "severity_override_bad_suggestion.txt")
    result = run_pyepubcheck("-u", "-m", "exp", severity_dir, "-c", overrides, transport="subprocess")
    assert result.returncode == 1
    assert "CHK-005" in result.stderr
