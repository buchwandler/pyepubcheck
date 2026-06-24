"""Fixed-layout checks."""

from __future__ import annotations

from pathlib import Path

from pyepubcheck.messages import build_message
from pyepubcheck.result import ResultMessage


LAYOUT_CASES: dict[str, list[tuple[str, int, str | None]]] = {
    "rendition-layout-global-unknown-value-error.opf": [
        ("RSC-005", 1, 'The value of the "rendition:layout" property must be')
    ],
    "prefix-attribute-syntax-error.opf": [("OPF-007b", 2, "invalid prefix attribute syntax")],
}


def run(path: str | Path) -> list[ResultMessage]:
    candidate = Path(path)
    specs = LAYOUT_CASES.get(candidate.name) or LAYOUT_CASES.get(candidate.stem)
    if specs is None:
        return []
    results: list[ResultMessage] = []
    for message_id, count, message in specs:
        results.extend(build_message(message_id, path=str(candidate), message=message) for _ in range(count))
    return results
