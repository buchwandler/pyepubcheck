"""Project-specific exceptions."""

from __future__ import annotations


class PyEpubcheckError(Exception):
    """Base error for pyepubcheck."""


class CLIUsageError(PyEpubcheckError):
    """Raised for invalid command-line usage."""
