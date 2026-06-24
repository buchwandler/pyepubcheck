"""Validation result models."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from pyepubcheck.models import PublicationItem, PublicationMetadata
from pyepubcheck.severity import Severity


@dataclass(frozen=True)
class ResultMessage:
    id: str
    severity: Severity
    message: str
    suggestion: str = ""
    path: str = ""
    line: int | None = None
    column: int | None = None
    element_id: str | None = None
    spec_ref: str | None = None


@dataclass
class ValidationReport:
    input_path: Path | str | None
    version: str
    profile: str
    messages: list[ResultMessage] = field(default_factory=list)
    items: list[PublicationItem] = field(default_factory=list)
    metadata: PublicationMetadata = field(default_factory=PublicationMetadata)

    def has_message(self, message_id: str, severity: Severity | None = None) -> bool:
        return any(
            message.id == message_id
            and (severity is None or message.severity is severity)
            for message in self.messages
        )

    def count_message(self, message_id: str) -> int:
        return sum(1 for message in self.messages if message.id == message_id)

    def exit_code(self, *, fail_on_warnings: bool = False) -> int:
        if any(message.severity in {Severity.FATAL, Severity.ERROR} for message in self.messages):
            return 1
        if fail_on_warnings and any(message.severity is Severity.WARNING for message in self.messages):
            return 1
        return 0
