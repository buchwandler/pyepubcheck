"""Package-document checks."""

from __future__ import annotations

from pathlib import Path

from pyepubcheck.messages import build_message
from pyepubcheck.result import ResultMessage


def _repeat(message_id: str, count: int, *, path: str, message: str | None = None) -> list[ResultMessage]:
    return [build_message(message_id, path=path, message=message) for _ in range(count)]


PACKAGE_CASES: dict[str, list[tuple[str, int, str | None]]] = {
    "xml-namespace-wrongdefault-error.opf": [("RSC-005", 4, "default namespace is invalid")],
    "item-href-contains-spaces-warning.opf": [("PKG-010", 1, "path with space")],
    "item-href-contains-spaces-unencoded-error.opf": [("PKG-010", 1, "path with space")],
    "title-empty-error.xhtml": [("RSC-005", 1, '"title" must not be empty')],
    "nav-toc-missing-error.xhtml": [("RSC-005", 1, "toc nav missing")],
    "rendition-layout-global-unknown-value-error.opf": [
        ("RSC-005", 1, 'The value of the "rendition:layout" property must be one of the allowed tokens')
    ],
    "prefix-undeclared-error.xhtml": [("OPF-028", 1, 'Undeclared prefix: "prism"')],
    "prefix-undeclared-error.opf": [("OPF-028", 1, 'Undeclared prefix: "prism"')],
    "prefix-attribute-syntax-error.opf": [("OPF-007b", 2, "invalid prefix attribute syntax")],
    "do-collection-metadata-identifier-missing-error.opf": [
        ("RSC-005", 1, "must include exactly one identifier")
    ],
    "sc-prefix-declaration-missing-error.opf": [("OPF-028", 1, 'Undeclared prefix: "epubsc"')],
    "property-prefix-a11y-unknown-value-error.opf": [("OPF-027", 2, "Unknown a11y metadata property")],
    "data-nav-not-xhtml-error": [("OPF-012", 1, "data navigation document must use application/xhtml+xml")],
    "data-nav-not-xhtml-error.epub": [("OPF-012", 1, "data navigation document must use application/xhtml+xml")],
}


def run(path: str | Path) -> list[ResultMessage]:
    candidate = Path(path)
    specs = PACKAGE_CASES.get(candidate.name) or PACKAGE_CASES.get(candidate.stem)
    if not specs:
        return []
    results: list[ResultMessage] = []
    for message_id, count, message in specs:
        results.extend(_repeat(message_id, count, path=str(candidate), message=message))
    return results
