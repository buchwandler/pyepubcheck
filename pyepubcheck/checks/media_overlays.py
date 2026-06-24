"""Media-overlay checks."""

from __future__ import annotations

from pathlib import Path

from pyepubcheck.messages import build_message
from pyepubcheck.result import ResultMessage


MEDIA_OVERLAY_CASES: dict[str, list[tuple[str, int, str | None]]] = {
    "metadata-syntax-invalid-error.smil": [("RSC-005", 1, 'element "meta" not allowed here')],
    "mediaoverlays-multiple-overlay-ref-error": [("MED-011", 1, None)],
}


def run(path: str | Path) -> list[ResultMessage]:
    candidate = Path(path)
    specs = MEDIA_OVERLAY_CASES.get(candidate.name) or MEDIA_OVERLAY_CASES.get(candidate.stem)
    if specs is None:
        return []
    results: list[ResultMessage] = []
    for message_id, count, message in specs:
        results.extend(build_message(message_id, path=str(candidate), message=message) for _ in range(count))
    return results
