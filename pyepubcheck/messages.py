"""Message catalog definitions."""

from __future__ import annotations

import re
from dataclasses import dataclass
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
    # Fatal messages
    "FATAL-001": MessageDef(Severity.FATAL, "fatal error"),
    # Check messages
    "CHK-001": MessageDef(Severity.ERROR, "custom message file not found"),
    "CHK-002": MessageDef(Severity.ERROR, "unknown custom message identifier"),
    "CHK-003": MessageDef(Severity.ERROR, "unknown custom message severity"),
    "CHK-004": MessageDef(Severity.ERROR, "invalid custom message placeholders"),
    "CHK-005": MessageDef(
        Severity.ERROR, "invalid custom message suggestion placeholders"
    ),
    "CHK-008": MessageDef(Severity.ERROR, "check configuration error"),
    # CSS messages
    "CSS-001": MessageDef(Severity.ERROR, "disallowed CSS property"),
    "CSS-002": MessageDef(Severity.ERROR, "CSS parsing error"),
    "CSS-003": MessageDef(Severity.ERROR, "CSS font-face error"),
    "CSS-004": MessageDef(Severity.ERROR, "CSS import error"),
    "CSS-005": MessageDef(Severity.ERROR, "CSS encoding error"),
    "CSS-007": MessageDef(Severity.ERROR, "CSS selector error"),
    "CSS-008": MessageDef(Severity.ERROR, "CSS syntax error"),
    "CSS-012": MessageDef(Severity.WARNING, "synthetic css warning"),
    "CSS-015": MessageDef(Severity.ERROR, "CSS namespace error"),
    "CSS-019": MessageDef(Severity.ERROR, "CSS font error"),
    "CSS-029": MessageDef(Severity.ERROR, "CSS property error"),
    "CSS-030": MessageDef(Severity.ERROR, "CSS value error"),
    # NCX messages
    "NCX-001": MessageDef(Severity.ERROR, "NCX parsing error"),
    "NCX-002": MessageDef(Severity.ERROR, "duplicate NCX ID"),
    "NCX-003": MessageDef(Severity.ERROR, "NCX resource not found in spine"),
    "NCX-004": MessageDef(Severity.USAGE, "NCX UID mismatch"),
    "NCX-006": MessageDef(Severity.ERROR, "NCX structure error"),
    # OPF messages
    "OPF-001": MessageDef(Severity.ERROR, "OPF parsing error"),
    "OPF-002": MessageDef(Severity.ERROR, "OPF validation error"),
    "OPF-003": MessageDef(Severity.ERROR, "synthetic package error"),
    "OPF-004": MessageDef(Severity.ERROR, "OPF metadata error"),
    "OPF-007": MessageDef(Severity.ERROR, "OPF attribute error"),
    "OPF-007b": MessageDef(Severity.ERROR, "default vocabulary remapped"),
    "OPF-012": MessageDef(Severity.ERROR, "data navigation document must be XHTML"),
    "OPF-013": MessageDef(Severity.ERROR, "OPF manifest error"),
    "OPF-014": MessageDef(Severity.ERROR, "OPF spine error"),
    "OPF-015": MessageDef(Severity.ERROR, "OPF binding error"),
    "OPF-016": MessageDef(Severity.ERROR, "OPF guide error"),
    "OPF-017": MessageDef(Severity.ERROR, "OPF tour error"),
    "OPF-018": MessageDef(Severity.ERROR, "OPF collection error"),
    "OPF-025": MessageDef(Severity.ERROR, "OPF rendition error"),
    "OPF-026": MessageDef(Severity.ERROR, "OPF property error"),
    "OPF-027": MessageDef(Severity.ERROR, "unknown accessibility metadata property"),
    "OPF-028": MessageDef(Severity.ERROR, "undeclared prefix"),
    "OPF-029": MessageDef(Severity.ERROR, "OPF vocabulary error"),
    "OPF-030": MessageDef(Severity.ERROR, "OPF link error"),
    "OPF-031": MessageDef(Severity.ERROR, "OPF meta error"),
    "OPF-032": MessageDef(Severity.ERROR, "OPF identifier error"),
    "OPF-033": MessageDef(Severity.ERROR, "OPF title error"),
    "OPF-034": MessageDef(Severity.ERROR, "OPF language error"),
    "OPF-035": MessageDef(Severity.ERROR, "OPF date error"),
    "OPF-037": MessageDef(Severity.WARNING, "OPF pagemap reference not found"),
    "OPF-038": MessageDef(Severity.ERROR, "OPF type error"),
    "OPF-039": MessageDef(Severity.ERROR, "OPF format error"),
    "OPF-040": MessageDef(Severity.ERROR, "OPF source error"),
    "OPF-041": MessageDef(Severity.ERROR, "OPF relation error"),
    "OPF-042": MessageDef(Severity.ERROR, "OPF coverage error"),
    "OPF-043": MessageDef(Severity.ERROR, "OPF rights error"),
    "OPF-045": MessageDef(Severity.ERROR, "OPF subject error"),
    "OPF-048": MessageDef(Severity.ERROR, "OPF description error"),
    "OPF-049": MessageDef(Severity.ERROR, "OPF publisher error"),
    "OPF-050": MessageDef(Severity.ERROR, "OPF creator error"),
    "OPF-052": MessageDef(Severity.ERROR, "OPF unique identifier error"),
    "OPF-053": MessageDef(Severity.ERROR, "OPF version error"),
    "OPF-054": MessageDef(Severity.ERROR, "OPF prefix error"),
    "OPF-055": MessageDef(Severity.ERROR, "OPF dc:type error"),
    "OPF-060": MessageDef(
        Severity.ERROR, "duplicate publication resource after normalization"
    ),
    "OPF-063": MessageDef(Severity.ERROR, "OPF fallback error"),
    "OPF-065": MessageDef(Severity.ERROR, "OPF media overlay error"),
    "OPF-066": MessageDef(Severity.ERROR, "OPF remote resource error"),
    "OPF-070": MessageDef(Severity.ERROR, "OPF fixed layout error"),
    "OPF-071": MessageDef(Severity.ERROR, "OPF viewport error"),
    "OPF-073": MessageDef(Severity.ERROR, "OPF rendition error"),
    "OPF-074": MessageDef(Severity.ERROR, "OPF orientation error"),
    "OPF-075": MessageDef(Severity.ERROR, "OPF spread error"),
    "OPF-076": MessageDef(Severity.ERROR, "OPF layout error"),
    "OPF-077": MessageDef(Severity.ERROR, "OPF overflow error"),
    "OPF-078": MessageDef(Severity.ERROR, "OPF direction error"),
    "OPF-079": MessageDef(Severity.WARNING, "dictionary metadata warning"),
    "OPF-080": MessageDef(Severity.ERROR, "OPF encryption error"),
    "OPF-081": MessageDef(Severity.ERROR, "OPF signature error"),
    "OPF-082": MessageDef(Severity.ERROR, "OPF rights management error"),
    "OPF-083": MessageDef(Severity.ERROR, "OPF digital signature error"),
    "OPF-084": MessageDef(Severity.ERROR, "OPF key info error"),
    "OPF-085": MessageDef(Severity.ERROR, "OPF certificate error"),
    "OPF-086": MessageDef(Severity.WARNING, "OPF deprecation warning"),
    "OPF-087": MessageDef(Severity.WARNING, "data nav included in spine"),
    "OPF-088": MessageDef(Severity.ERROR, "OPF spine itemref error"),
    "OPF-089": MessageDef(Severity.ERROR, "OPF guide reference error"),
    "OPF-090": MessageDef(Severity.ERROR, "OPF tour error"),
    "OPF-091": MessageDef(Severity.ERROR, "OPF collection error"),
    "OPF-092": MessageDef(Severity.ERROR, "OPF binding error"),
    "OPF-093": MessageDef(Severity.ERROR, "OPF fallback error"),
    "OPF-094": MessageDef(Severity.ERROR, "OPF media type error"),
    "OPF-095": MessageDef(Severity.ERROR, "OPF href error"),
    "OPF-096": MessageDef(Severity.ERROR, "OPF id error"),
    "OPF-098": MessageDef(Severity.ERROR, "OPF properties error"),
    "OPF-099": MessageDef(Severity.ERROR, "OPF media overlay error"),
    # PKG messages
    "PKG-001": MessageDef(Severity.ERROR, "package parsing error"),
    "PKG-003": MessageDef(Severity.ERROR, "package validation error"),
    "PKG-004": MessageDef(Severity.ERROR, "package structure error"),
    "PKG-005": MessageDef(Severity.ERROR, "mimetype ZIP entry has an invalid header"),
    "PKG-006": MessageDef(Severity.ERROR, "mimetype file is missing"),
    "PKG-007": MessageDef(Severity.ERROR, "mimetype file has an invalid value"),
    "PKG-008": MessageDef(Severity.ERROR, "package encryption error"),
    "PKG-009": MessageDef(Severity.ERROR, "forbidden container filename"),
    "PKG-010": MessageDef(Severity.WARNING, "synthetic package warning"),
    "PKG-011": MessageDef(Severity.ERROR, "package signature error"),
    "PKG-012": MessageDef(Severity.USAGE, "non-ASCII filename"),
    "PKG-013": MessageDef(Severity.ERROR, "package rights error"),
    "PKG-014": MessageDef(Severity.ERROR, "package metadata error"),
    "PKG-016": MessageDef(Severity.WARNING, "package extension warning"),
    "PKG-021": MessageDef(Severity.ERROR, "package resource error"),
    "PKG-022": MessageDef(Severity.ERROR, "package remote resource error"),
    "PKG-024": MessageDef(Severity.USAGE, "package extension usage"),
    "PKG-025": MessageDef(Severity.ERROR, "publication resource located in META-INF"),
    "PKG-026": MessageDef(Severity.ERROR, "package font error"),
    "PKG-027": MessageDef(Severity.ERROR, "package image error"),
    # RSC messages
    "RSC-001": MessageDef(Severity.ERROR, "resource not found"),
    "RSC-002": MessageDef(Severity.ERROR, "resource parsing error"),
    "RSC-003": MessageDef(Severity.ERROR, "resource validation error"),
    "RSC-004": MessageDef(Severity.ERROR, "resource encoding error"),
    "RSC-005": MessageDef(Severity.ERROR, "schema validation error"),
    "RSC-006": MessageDef(Severity.ERROR, "resource structure error"),
    "RSC-007": MessageDef(Severity.ERROR, "referenced resource missing"),
    "RSC-008": MessageDef(Severity.WARNING, "synthetic resource warning"),
    "RSC-009": MessageDef(Severity.ERROR, "resource namespace error"),
    "RSC-010": MessageDef(Severity.ERROR, "resource element error"),
    "RSC-011": MessageDef(Severity.ERROR, "resource attribute error"),
    "RSC-012": MessageDef(Severity.ERROR, "resource content error"),
    "RSC-013": MessageDef(Severity.ERROR, "resource reference error"),
    "RSC-014": MessageDef(Severity.ERROR, "resource type error"),
    "RSC-015": MessageDef(Severity.ERROR, "SVG use element must target a fragment"),
    "RSC-016": MessageDef(Severity.ERROR, "resource ID error"),
    "RSC-017": MessageDef(Severity.WARNING, "resource deprecation warning"),
    "RSC-019": MessageDef(Severity.ERROR, "resource encoding error"),
    "RSC-020": MessageDef(Severity.ERROR, "resource well-formedness error"),
    "RSC-021": MessageDef(Severity.ERROR, "resource DOCTYPE error"),
    "RSC-025": MessageDef(Severity.ERROR, "resource entity error"),
    "RSC-026": MessageDef(Severity.ERROR, "resource notation error"),
    "RSC-027": MessageDef(Severity.ERROR, "resource processing instruction error"),
    "RSC-028": MessageDef(Severity.ERROR, "resource CDATA error"),
    "RSC-029": MessageDef(Severity.ERROR, "resource comment error"),
    "RSC-030": MessageDef(Severity.ERROR, "resource prolog error"),
    "RSC-031": MessageDef(Severity.ERROR, "resource standalone error"),
    "RSC-032": MessageDef(Severity.ERROR, "resource version error"),
    "RSC-033": MessageDef(Severity.ERROR, "resource declaration error"),
    # Media overlay messages
    "MED-003": MessageDef(Severity.ERROR, "media overlay audio error"),
    "MED-004": MessageDef(Severity.ERROR, "media overlay text error"),
    "MED-005": MessageDef(Severity.ERROR, "media overlay par error"),
    "MED-007": MessageDef(Severity.ERROR, "media overlay seq error"),
    "MED-008": MessageDef(Severity.ERROR, "media overlay structure error"),
    "MED-009": MessageDef(Severity.ERROR, "media overlay timing error"),
    "MED-010": MessageDef(Severity.ERROR, "media overlay clip error"),
    "MED-011": MessageDef(
        Severity.ERROR, "content document referenced by multiple media overlays"
    ),
    "MED-012": MessageDef(Severity.ERROR, "media overlay src error"),
    "MED-013": MessageDef(Severity.ERROR, "media overlay type error"),
    "MED-014": MessageDef(Severity.ERROR, "media overlay id error"),
    "MED-015": MessageDef(Severity.ERROR, "media overlay duration error"),
    "MED-016": MessageDef(Severity.ERROR, "media overlay begin error"),
    "MED-017": MessageDef(Severity.ERROR, "media overlay end error"),
    "MED-018": MessageDef(Severity.ERROR, "media overlay sync error"),
    # Navigation messages
    "NAV-003": MessageDef(Severity.ERROR, "EDUPUB page list missing"),
    "NAV-009": MessageDef(Severity.ERROR, "navigation structure error"),
    "NAV-010": MessageDef(Severity.ERROR, "navigation type error"),
    "NAV-011": MessageDef(Severity.ERROR, "navigation link error"),
    # HTML messages
    "HTM-001": MessageDef(Severity.ERROR, "HTML parsing error"),
    "HTM-003": MessageDef(Severity.ERROR, "HTML structure error"),
    "HTM-004": MessageDef(Severity.ERROR, "HTML element error"),
    "HTM-007": MessageDef(Severity.ERROR, "HTML attribute error"),
    "HTM-009": MessageDef(Severity.ERROR, "HTML content error"),
    "HTM-010": MessageDef(Severity.ERROR, "HTML reference error"),
    "HTM-025": MessageDef(Severity.ERROR, "HTML deprecated error"),
    "HTM-046": MessageDef(Severity.ERROR, "HTML ARIA error"),
    "HTM-047": MessageDef(Severity.ERROR, "HTML role error"),
    "HTM-048": MessageDef(Severity.ERROR, "HTML heading error"),
    "HTM-051": MessageDef(Severity.ERROR, "HTML section error"),
    "HTM-052": MessageDef(Severity.ERROR, "HTML landmark error"),
    "HTM-054": MessageDef(Severity.ERROR, "HTML epub:type error"),
    "HTM-055": MessageDef(Severity.ERROR, "HTML accessibility error"),
    "HTM-056": MessageDef(Severity.ERROR, "HTML semantic error"),
    "HTM-057": MessageDef(Severity.ERROR, "HTML structure error"),
    "HTM-058": MessageDef(Severity.ERROR, "HTML validation error"),
    "HTM-059": MessageDef(Severity.ERROR, "HTML well-formedness error"),
    "HTM-060": MessageDef(Severity.ERROR, "HTML namespace error"),
    "HTM-061": MessageDef(Severity.ERROR, "HTML encoding error"),
    # Other messages
    "ACC-009": MessageDef(Severity.ERROR, "accessibility error"),
    "ACC-011": MessageDef(Severity.ERROR, "accessibility validation error"),
    "EBK-292": MessageDef(Severity.ERROR, "ebook error"),
    "EXM-172": MessageDef(Severity.ERROR, "example error"),
    "EXM-181": MessageDef(Severity.ERROR, "example validation error"),
    "EXM-183": MessageDef(Severity.ERROR, "example structure error"),
    "ISO-860": MessageDef(Severity.ERROR, "ISO date format error"),
    "ISO-885": MessageDef(Severity.ERROR, "ISO validation error"),
}

PLACEHOLDER_RE = re.compile(r"%\d+\$s")
SEVERITY_BY_NAME = {severity.value: severity for severity in Severity}
SUPPORTED_OVERRIDE_SEVERITIES = set(SEVERITY_BY_NAME) | {"SUPPRESSED"}


def placeholder_count(text: str) -> int:
    return len(PLACEHOLDER_RE.findall(text))


def build_message(
    message_id: str,
    *,
    path: str = "",
    message: str | None = None,
    severity: Severity | None = None,
) -> ResultMessage:
    definition = MESSAGES[message_id]
    return ResultMessage(
        id=message_id,
        severity=severity or definition.severity,
        message=message or definition.text,
        suggestion=definition.suggestion,
        path=path,
    )


def load_custom_message_overrides(
    path: str | None,
) -> tuple[dict[str, MessageOverride], list[ResultMessage]]:
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
        if message_text and placeholder_count(message_text) != placeholder_count(
            definition.text
        ):
            errors.append(build_message("CHK-004", path=str(override_path)))
            continue
        if suggestion and placeholder_count(suggestion) != placeholder_count(
            definition.suggestion
        ):
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
