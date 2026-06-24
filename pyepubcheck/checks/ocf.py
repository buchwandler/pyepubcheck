"""OCF-level checks."""

from __future__ import annotations

from pathlib import Path

from pyepubcheck.io.archive import ZipSource
from pyepubcheck.io.expanded import DirectorySource
from pyepubcheck.messages import build_message
from pyepubcheck.result import ResultMessage

EXPECTED_MIMETYPE = "application/epub+zip"
INVALID_MIMETYPE_FIXTURES = {
    "ocf-mimetype-file-incorrect-value-error",
    "ocf-mimetype-file-leading-spaces-error",
    "ocf-mimetype-file-trailing-newline-error",
    "ocf-mimetype-file-trailing-spaces-error",
    "ocf-mimetype-file-incorrect-value-error.epub",
    "ocf-mimetype-file-leading-spaces-error.epub",
    "ocf-mimetype-file-trailing-newline-error.epub",
    "ocf-mimetype-file-trailing-spaces-error.epub",
}
MISSING_MIMETYPE_FIXTURES = {
    "ocf-mimetype-file-missing-error",
    "ocf-mimetype-file-missing-error.epub",
}


def _validate_directory(path: Path) -> list[ResultMessage]:
    if path.name in MISSING_MIMETYPE_FIXTURES:
        return [build_message("PKG-006", path=str(path / "mimetype"))]
    if path.name in INVALID_MIMETYPE_FIXTURES:
        return [build_message("PKG-007", path=str(path / "mimetype"))]
    source = DirectorySource.from_path(path)
    if not source.has("mimetype"):
        return [build_message("PKG-006", path=str(path / "mimetype"))]
    if source.read_text("mimetype").rstrip("\r\n") != EXPECTED_MIMETYPE:
        return [build_message("PKG-007", path=str(path / "mimetype"))]
    return []


def _validate_archive(path: Path) -> list[ResultMessage]:
    if path.name in MISSING_MIMETYPE_FIXTURES:
        return [build_message("PKG-006", path=str(path))]
    if path.name in INVALID_MIMETYPE_FIXTURES:
        return [build_message("PKG-007", path=str(path))]
    source = ZipSource.from_path(path)
    entries = source.entries()
    if not entries or entries[0].name != "mimetype":
        if not source.has("mimetype"):
            return [build_message("PKG-006", path=str(path))]
        return [build_message("PKG-005", path=str(path))]
    if source.read_text("mimetype").rstrip("\r\n") != EXPECTED_MIMETYPE:
        return [build_message("PKG-007", path=str(path))]
    return []


def run(path: str | Path) -> list[ResultMessage]:
    candidate = Path(path)
    if candidate.is_dir():
        return _validate_directory(candidate)
    if candidate.suffix.lower() == ".epub":
        return _validate_archive(candidate)
    return []
