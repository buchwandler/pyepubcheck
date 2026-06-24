"""Message catalog definitions."""

from __future__ import annotations

from dataclasses import dataclass
import re
from pathlib import Path

from pyepubcheck.result import ResultMessage
from pyepubcheck.severity import Severity


@dataclass(frozen=True)
class MessageDef:
    severity: Severity
    text: str
    suggestion: str = ""


@dataclass(frozen=True)
class MessageOverride:
    severity: Severity | None
    text: str | None = None
    suggestion: str | None = None
    suppressed: bool = False


MESSAGES: dict[str, MessageDef] = {
    "CHK-001": MessageDef(Severity.ERROR, "custom message file not found"),
    "CHK-002": MessageDef(Severity.ERROR, "unknown custom message identifier"),
    "CHK-003": MessageDef(Severity.ERROR, "unknown custom message severity"),
    "CHK-004": MessageDef(Severity.ERROR, "invalid custom message placeholders"),
    "CHK-005": MessageDef(Severity.ERROR, "invalid custom suggestion placeholders"),
    "CSS-012": MessageDef(Severity.WARNING, "synthetic css warning"),
    "CSS-001": MessageDef(Severity.ERROR, "disallowed CSS property"),
    "CSS-008": MessageDef(Severity.ERROR, "CSS syntax error"),
    "NCX-004": MessageDef(Severity.USAGE, "usage information"),
    "OPF-003": MessageDef(Severity.ERROR, "synthetic package error"),
    "OPF-007b": MessageDef(Severity.ERROR, "default vocabulary remapped"),
    "OPF-012": MessageDef(Severity.ERROR, "data navigation document must be XHTML"),
    "OPF-027": MessageDef(Severity.ERROR, "unknown accessibility metadata property"),
    "OPF-028": MessageDef(Severity.ERROR, "undeclared prefix"),
    "OPF-060": MessageDef(Severity.ERROR, "duplicate publication resource after normalization"),
    "OPF-079": MessageDef(Severity.WARNING, "dictionary metadata warning"),
    "PKG-005": MessageDef(Severity.ERROR, "mimetype ZIP entry has an invalid header"),
    "PKG-006": MessageDef(Severity.ERROR, "mimetype file is missing"),
    "PKG-007": MessageDef(Severity.ERROR, "mimetype file has an invalid value"),
    "PKG-009": MessageDef(Severity.ERROR, "forbidden container filename"),
    "PKG-010": MessageDef(Severity.WARNING, "synthetic package warning"),
    "PKG-025": MessageDef(Severity.ERROR, "publication resource located in META-INF"),
    "RSC-008": MessageDef(Severity.WARNING, "synthetic resource warning"),
    "RSC-005": MessageDef(Severity.ERROR, "schema validation error"),
    "RSC-007": MessageDef(Severity.ERROR, "referenced resource missing"),
    "RSC-015": MessageDef(Severity.ERROR, "SVG use element must target a fragment"),
    "MED-011": MessageDef(Severity.ERROR, "content document referenced by multiple media overlays"),
    "NAV-003": MessageDef(Severity.ERROR, "EDUPUB page list missing"),
}

PLACEHOLDER_RE = re.compile(r"%\d+\$s")
SEVERITY_BY_NAME = {
    severity.value: severity
    for severity in Severity
}
SUPPORTED_OVERRIDE_SEVERITIES = set(SEVERITY_BY_NAME) | {"SUPPRESSED"}


def placeholder_count(text: str) -> int:
    return len(PLACEHOLDER_RE.findall(text))


def build_message(message_id: str, *, path: str = "", message: str | None = None, severity: Severity | None = None) -> ResultMessage:
    definition = MESSAGES[message_id]
    return ResultMessage(
        id=message_id,
        severity=severity or definition.severity,
        message=message or definition.text,
        suggestion=definition.suggestion,
        path=path,
    )


def load_custom_message_overrides(path: str | None) -> tuple[dict[str, MessageOverride], list[ResultMessage]]:
    if not path:
        return {}, []
    override_path = Path(path)
    if not override_path.is_file():
        return {}, [build_message("CHK-001", path=str(override_path))]

    overrides: dict[str, MessageOverride] = {}
    errors: list[ResultMessage] = []
    lines = override_path.read_text(encoding="utf-8").splitlines()
    for raw_line in lines[1:]:
        if not raw_line.strip():
            continue
        columns = raw_line.split("\t")
        columns.extend([""] * (4 - len(columns)))
        message_id, severity_name, message_text, suggestion = columns[:4]
        if message_id not in MESSAGES:
            errors.append(build_message("CHK-002", path=str(override_path)))
            continue
        if severity_name not in SUPPORTED_OVERRIDE_SEVERITIES:
            errors.append(build_message("CHK-003", path=str(override_path)))
            continue

        definition = MESSAGES[message_id]
        if message_text and placeholder_count(message_text) != placeholder_count(definition.text):
            errors.append(build_message("CHK-004", path=str(override_path)))
            continue
        if suggestion and placeholder_count(suggestion) != placeholder_count(definition.suggestion):
            errors.append(build_message("CHK-005", path=str(override_path)))
            continue

        overrides[message_id] = MessageOverride(
            severity=SEVERITY_BY_NAME.get(severity_name),
            text=message_text or None,
            suggestion=suggestion or None,
            suppressed=severity_name == "SUPPRESSED",
        )
    return overrides, errors


def apply_custom_message_overrides(
    messages: list[ResultMessage],
    overrides: dict[str, MessageOverride],
) -> list[ResultMessage]:
    updated: list[ResultMessage] = []
    for message in messages:
        override = overrides.get(message.id)
        if override is None:
            updated.append(message)
            continue
        if override.suppressed:
            continue
        updated.append(
            ResultMessage(
                id=message.id,
                severity=override.severity or message.severity,
                message=override.text or message.message,
                suggestion=override.suggestion or message.suggestion,
                path=message.path,
                line=message.line,
                column=message.column,
                element_id=message.element_id,
                spec_ref=message.spec_ref,
            )
        )
    return updated
