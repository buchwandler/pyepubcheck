"""Directory-based publication sources."""

from __future__ import annotations

import zipfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DirectorySource:
    path: Path

    @classmethod
    def from_path(cls, path: str | Path) -> DirectorySource:
        return cls(Path(path))

    def has(self, relative_path: str) -> bool:
        return (self.path / relative_path).is_file()

    def read_text(self, relative_path: str) -> str:
        return (self.path / relative_path).read_text(encoding="utf-8")

    def save(self, output_path: Path | None = None) -> Path:
        destination = output_path or self.path.with_suffix(".epub")
        mimetype = self.path / "mimetype"
        with zipfile.ZipFile(destination, "w") as archive:
            if mimetype.is_file():
                archive.writestr(
                    "mimetype",
                    mimetype.read_text(encoding="utf-8").rstrip("\r\n"),
                    compress_type=zipfile.ZIP_STORED,
                )
            for child in sorted(self.path.rglob("*")):
                if not child.is_file() or child == mimetype:
                    continue
                archive.write(child, child.relative_to(self.path).as_posix())
        return destination
