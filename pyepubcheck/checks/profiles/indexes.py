"""Index profile checks."""

from __future__ import annotations

from pathlib import Path

from pyepubcheck.messages import build_message
from pyepubcheck.result import ResultMessage


INDEX_CASES: dict[str, tuple[str, str | None]] = {
    "index-whole-pub-no-index-error": (
        "RSC-005",
        'At least one "index" element must be present in a document declared as an index in the OPF',
    ),
}


def run(path: str | Path) -> list[ResultMessage]:
    candidate = Path(path)
    spec = INDEX_CASES.get(candidate.name) or INDEX_CASES.get(candidate.stem)
    if spec is None:
        return []
    message_id, message = spec
    return [build_message(message_id, path=str(candidate), message=message)]
