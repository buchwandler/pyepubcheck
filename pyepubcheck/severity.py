"""Severity levels used in validation results."""

from __future__ import annotations

from enum import Enum


class Severity(str, Enum):
    FATAL = "FATAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    USAGE = "USAGE"

    @classmethod
    def reporting_order(cls) -> tuple["Severity", ...]:
        return (
            cls.FATAL,
            cls.ERROR,
            cls.WARNING,
            cls.INFO,
            cls.USAGE,
        )
