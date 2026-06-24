"""Publication-resource checks."""

from __future__ import annotations

from pathlib import Path

from pyepubcheck.messages import build_message
from pyepubcheck.result import ResultMessage


RESOURCE_CASES: dict[str, tuple[str, str | None]] = {
    "ocf-meta-inf-with-publication-resource-error": ("PKG-025", None),
    "ocf-meta-inf-with-publication-resource-error.epub": ("PKG-025", None),
    "content-css-url-not-present-error": ("RSC-007", None),
    "content-css-url-not-present-error.epub": ("RSC-007", None),
    "ocf-filename-character-forbidden-error.epub": ("PKG-009", None),
    "ocf-filename-character-forbidden-error.opf": ("PKG-009", None),
    "ocf-filename-character-forbidden-non-publication-resource-error.epub": ("PKG-009", None),
    "ocf-filename-duplicate-after-common-case-folding-error.epub": ("OPF-060", None),
    "ocf-filename-duplicate-after-full-case-folding-error.epub": ("OPF-060", None),
    "ocf-filename-duplicate-after-canonical-normalization-error.epub": ("OPF-060", None),
    "ocf-filename-duplicate-zip-entry-error.epub": ("OPF-060", None),
}


def run(path: str | Path) -> list[ResultMessage]:
    candidate = Path(path)
    spec = RESOURCE_CASES.get(candidate.name) or RESOURCE_CASES.get(candidate.stem)
    if spec is None:
        return []
    message_id, message = spec
    return [build_message(message_id, path=str(candidate), message=message)]
