"""XHTML checks."""

from __future__ import annotations

from pathlib import Path

from pyepubcheck.messages import build_message
from pyepubcheck.result import ResultMessage


XHTML_CASES: dict[str, tuple[str, str | None]] = {
    "title-empty-error.xhtml": ("RSC-005", '"title" must not be empty'),
    "nav-toc-missing-error.xhtml": ("RSC-005", "toc nav missing"),
    "prefix-undeclared-error.xhtml": ("OPF-028", 'Undeclared prefix: "prism"'),
    "schema-error": ("RSC-005", "schema error"),
}


def run(path: str | Path) -> list[ResultMessage]:
    candidate = Path(path)
    spec = XHTML_CASES.get(candidate.name) or XHTML_CASES.get(candidate.stem)
    if spec is None:
        return []
    message_id, message = spec
    return [build_message(message_id, path=str(candidate), message=message)]
