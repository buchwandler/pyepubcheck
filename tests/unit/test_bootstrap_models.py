from __future__ import annotations

from pathlib import Path

from pyepubcheck.config import ValidationConfig
from pyepubcheck.result import ResultMessage, ValidationReport
from pyepubcheck.severity import Severity


def test_validation_report_exit_code_tracks_errors() -> None:
    report = ValidationReport(input_path=Path("book.epub"), version="3.0", profile="default")
    assert report.exit_code() == 0
    report.messages.append(ResultMessage(id="PKG-001", severity=Severity.ERROR, message="broken"))
    assert report.exit_code() == 1


def test_validation_report_fail_on_warnings() -> None:
    report = ValidationReport(input_path=Path("book.epub"), version="3.0", profile="default")
    report.messages.append(ResultMessage(id="PKG-010", severity=Severity.WARNING, message="warn"))
    assert report.exit_code() == 0
    assert report.exit_code(fail_on_warnings=True) == 1


def test_validation_config_defaults() -> None:
    config = ValidationConfig()
    assert config.mode == "auto"
    assert config.profile == "default"
