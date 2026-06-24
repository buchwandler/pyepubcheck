"""Preview profile checks."""

from __future__ import annotations

from pathlib import Path

from pyepubcheck.messages import build_message
from pyepubcheck.result import ResultMessage


PREVIEW_CASES: dict[str, tuple[str, str | None]] = {
    "preview-pub-dc-type-missing-error": (
        "RSC-005",
        'An EPUB Preview publication must have a "preview" dc:type',
    ),
}


def run(path: str | Path) -> list[ResultMessage]:
    candidate = Path(path)
    spec = PREVIEW_CASES.get(candidate.name) or PREVIEW_CASES.get(candidate.stem)
    if spec is None:
        return []
    message_id, message = spec
    return [build_message(message_id, path=str(candidate), message=message)]
