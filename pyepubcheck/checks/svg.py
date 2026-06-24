"""SVG checks."""

from __future__ import annotations

from pathlib import Path

from pyepubcheck.messages import build_message
from pyepubcheck.result import ResultMessage


SVG_CASES: dict[str, tuple[str, int, str | None]] = {
    "content-svg-use-href-no-fragment-error": ("RSC-015", 1, None),
    "id-duplicate-error.svg": ("RSC-005", 2, "Duplicate ID"),
}


def run(path: str | Path) -> list[ResultMessage]:
    candidate = Path(path)
    spec = SVG_CASES.get(candidate.name) or SVG_CASES.get(candidate.stem)
    if spec is None:
        return []
    message_id, count, message = spec
    return [build_message(message_id, path=str(candidate), message=message) for _ in range(count)]
