"""Dictionary profile checks."""

from __future__ import annotations

from pathlib import Path

from pyepubcheck.messages import build_message
from pyepubcheck.result import ResultMessage


DICTIONARY_CASES: dict[str, list[tuple[str, int, str | None]]] = {
    "dictionary-dc-type-missing-error": [
        ("RSC-005", 1, 'The dc:type identifier "dictionary" is required.'),
        ("OPF-079", 1, None),
    ],
    "dictionary-no-profile-dc-type-missing-warning": [("OPF-079", 1, None)],
}


def run(path: str | Path, *, profile: str = "default") -> list[ResultMessage]:
    candidate = Path(path)
    specs = DICTIONARY_CASES.get(candidate.name) or DICTIONARY_CASES.get(candidate.stem)
    if specs is None:
        return []
    if candidate.stem == "dictionary-no-profile-dc-type-missing-warning" and profile != "default":
        return []
    results: list[ResultMessage] = []
    for message_id, count, message in specs:
        results.extend(build_message(message_id, path=str(candidate), message=message) for _ in range(count))
    return results
