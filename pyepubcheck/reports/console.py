"""Console rendering."""

from __future__ import annotations

from pyepubcheck.i18n import success_message
from pyepubcheck.result import ValidationReport
from pyepubcheck.severity import Severity


def render_console(
    report: ValidationReport,
    *,
    locale: str | None = None,
    messages: list | None = None,
) -> tuple[str, str]:
    selected = report.messages if messages is None else messages
    stdout_lines: list[str] = []
    stderr_lines: list[str] = []

    # Add version info header
    from pyepubcheck import __version__

    stdout_lines.append(f"EPUBCheck v{__version__}")

    for message in selected:
        line = f"{message.severity.value}({message.id}): {message.message}"
        if message.severity in {Severity.WARNING, Severity.ERROR, Severity.FATAL}:
            stderr_lines.append(line)
        else:
            stdout_lines.append(line)
    if not selected:
        stdout_lines.append(success_message(locale))
    return ("\n".join(stdout_lines), "\n".join(stderr_lines))
