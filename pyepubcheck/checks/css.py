"""CSS checks."""

from __future__ import annotations

from pathlib import Path

from pyepubcheck.messages import build_message
from pyepubcheck.result import ResultMessage


CSS_CASES: dict[str, list[tuple[str, str | None]]] = {
    "content-css-url-not-present-error": [("RSC-007", None)],
    "content-css-property-direction-error": [("CSS-001", "direction")],
    "css-error": [("CSS-008", "css error")],
}


def run(path: str | Path) -> list[ResultMessage]:
    candidate = Path(path)
    specs = CSS_CASES.get(candidate.name) or CSS_CASES.get(candidate.stem)
    if specs is None:
        return []
    return [
        build_message(message_id, path=str(candidate), message=message)
        for message_id, message in specs
    ]
