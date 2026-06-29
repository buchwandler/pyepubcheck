from __future__ import annotations

from pathlib import Path

import pytest


def _cli_fixture(fixtures, name: str) -> Path:
    return fixtures.fixture_path("/cli/files", name)


# specmason: @scenario-EPUBCHECK-17C84E51
def test_version_with_input_prints_version_and_success(
    run_pyepubcheck, fixtures
) -> None:
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck("--version", valid, transport="subprocess")
    assert result.returncode == 0
    assert result.stdout.startswith("EPUBCheck v0.1.0")
    assert "No errors or warnings detected." in result.stdout


# specmason: @scenario-EPUBCHECK-1BE1F6F7
def test_quiet_mode_allows_saving_xml_report(run_pyepubcheck, fixtures) -> None:
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck(
        valid, "--quiet", "-o", "report.xml", transport="subprocess"
    )
    assert result.returncode == 0
    assert result.stdout == ""
    assert result.xml_report is not None


# specmason: @scenario-EPUBCHECK-B406E70A
def test_conflicting_report_formats_are_rejected(
    run_pyepubcheck, fixtures, tmp_path: Path
) -> None:
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck(
        valid,
        "-o",
        "report.xml",
        "-j",
        "report.json",
        transport="subprocess",
    )
    assert result.returncode == 1
    assert "Only one output format can be specified at a time." in result.stderr
    assert not (tmp_path / "report.xml").exists()
    assert not (tmp_path / "report.json").exists()


# specmason: @scenario-EPUBCHECK-B3C07913
def test_failonwarnings_returns_error(run_pyepubcheck, fixtures) -> None:
    warning_dir = _cli_fixture(fixtures, "20-warning-tester")
    result = run_pyepubcheck(
        "--failonwarnings", "-m", "exp", warning_dir, transport="subprocess"
    )
    assert result.returncode == 1
    assert "WARNING(PKG-010)" in result.stderr


# specmason: @scenario-EPUBCHECK-69B78FC4
def test_usage_flag_includes_usage_messages(run_pyepubcheck, fixtures) -> None:
    severity_dir = _cli_fixture(fixtures, "20-severity-tester")
    result = run_pyepubcheck("-u", "-m", "exp", severity_dir, transport="subprocess")
    assert result.returncode == 1
    assert "USAGE(NCX-004)" in result.stdout


@pytest.mark.parametrize(
    ("flag", "expected_returncode", "present", "absent"),
    [
        ("-w", 1, ("WARNING(PKG-010)", "ERROR(OPF-003)"), ("USAGE(",)),
        ("-e", 1, ("ERROR(OPF-003)",), ("WARNING(", "USAGE(")),
        ("-f", 0, (), ("WARNING(", "ERROR(", "USAGE(")),
    ],
)
# specmason: @scenario-EPUBCHECK-3664BAA6
def test_severity_filters(
    run_pyepubcheck,
    fixtures,
    flag: str,
    expected_returncode: int,
    present: tuple[str, ...],
    absent: tuple[str, ...],
) -> None:
    severity_dir = _cli_fixture(fixtures, "20-severity-tester")
    result = run_pyepubcheck(flag, "-m", "exp", severity_dir, transport="subprocess")
    assert result.returncode == expected_returncode
    for text in present:
        assert text in result.stderr
    for text in absent:
        assert text not in result.stdout
        assert text not in result.stderr


# specmason: @scenario-EPUBCHECK-8F47AA55
def test_json_stdout_report_suppresses_success_message(
    run_pyepubcheck, fixtures
) -> None:
    valid = _cli_fixture(fixtures, "valid.epub")
    result = run_pyepubcheck(valid, "-j", "-", transport="subprocess")
    assert result.returncode == 0
    assert result.json_report is not None
    assert result.json_report["title"] == "Minimal EPUB 3.0"
    assert "No errors or warnings detected." not in result.stdout


# specmason: @scenario-EPUBCHECK-785ABF9C
def test_custom_message_overrides_apply(run_pyepubcheck, fixtures) -> None:
    severity_dir = _cli_fixture(fixtures, "20-severity-tester")
    overrides = _cli_fixture(fixtures, "severity_override.txt")
    result = run_pyepubcheck(
        "-u", "-m", "exp", severity_dir, "-c", overrides, transport="subprocess"
    )
    assert result.returncode == 1
    assert "USAGE(" not in result.stdout
    assert "WARNING(" not in result.stderr
    assert "ERROR(" in result.stderr
    assert "This is an overridden message" in result.stderr


@pytest.mark.parametrize(
    ("filename", "expected_code"),
    [
        ("severity_override_missing.txt", "CHK-001"),
        ("severity_override_bad_id.txt", "CHK-002"),
        ("severity_override_bad_severity.txt", "CHK-003"),
        ("severity_override_bad_message.txt", "CHK-004"),
        ("severity_override_bad_suggestion.txt", "CHK-005"),
    ],
)
# specmason: @scenario-EPUBCHECK-708BF7A2
def test_custom_message_validation_errors(
    run_pyepubcheck, fixtures, filename: str, expected_code: str
) -> None:
    severity_dir = _cli_fixture(fixtures, "20-severity-tester")
    override_path = _cli_fixture(fixtures, filename)
    result = run_pyepubcheck(
        "-u", "-m", "exp", severity_dir, "-c", override_path, transport="subprocess"
    )
    assert result.returncode == 1
    assert f"ERROR({expected_code})" in result.stderr
