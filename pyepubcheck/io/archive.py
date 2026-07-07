"""ZIP-based publication sources."""

from __future__ import annotations

import zipfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ZipEntry:
    name: str
    compress_type: int


@dataclass(frozen=True)
class ZipSource:
    path: Path

    @classmethod
    def from_path(cls, path: str | Path) -> ZipSource:
        return cls(Path(path))

    def entries(self) -> list[ZipEntry]:
        with zipfile.ZipFile(self.path) as archive:
            return [ZipEntry(info.filename, info.compress_type) for info in archive.infolist()]

    def has(self, name: str) -> bool:
        return any(entry.name == name for entry in self.entries())

    def read_text(self, name: str) -> str:
        with zipfile.ZipFile(self.path) as archive:
            return archive.read(name).decode("utf-8")
