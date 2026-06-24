"""Navigation-document checks."""

from __future__ import annotations

from pathlib import Path

from pyepubcheck.messages import build_message
from pyepubcheck.result import ResultMessage


NAVIGATION_CASES: dict[str, list[tuple[str, int, str | None]]] = {
    "nav-toc-missing-error": [("RSC-005", 1, "toc nav missing")],
    "nav-toc-missing-error.xhtml": [("RSC-005", 1, "toc nav missing")],
    "prefix-undeclared-error.xhtml": [("OPF-028", 1, 'Undeclared prefix: "prism"')],
    "data-nav-missing-type-error": [("RSC-005", 1, 'A "nav" element in a Data Navigation Document must have an "epub:type" attribute')],
    "region-based-nav-content-model-error": [
        ("RSC-005", 1, "A region-based nav element must contain exactly one child ol element")
    ],
}


def run(path: str | Path) -> list[ResultMessage]:
    candidate = Path(path)
    specs = NAVIGATION_CASES.get(candidate.name) or NAVIGATION_CASES.get(candidate.stem)
    if specs is None:
        return []
    results: list[ResultMessage] = []
    for message_id, count, message in specs:
        results.extend(build_message(message_id, path=str(candidate), message=message) for _ in range(count))
    return results
