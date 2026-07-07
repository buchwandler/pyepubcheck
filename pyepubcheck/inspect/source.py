"""Read-only publication sources for inspection."""

from __future__ import annotations

import posixpath
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Protocol
from urllib.parse import unquote


@dataclass(frozen=True)
class SourceEntry:
    path: str
    size_bytes: int
    compressed_size_bytes: int | None
    compress_type: int | None


class PublicationSource(Protocol):
    root: Path
    kind: str

    def exists(self, path: str) -> bool: ...

    def read_bytes(self, path: str) -> bytes: ...

    def read_text(self, path: str, encoding: str = "utf-8") -> str: ...

    def entries(self) -> list[SourceEntry]: ...


def _normalize_relative_path(path: str) -> str:
    normalized = posixpath.normpath(path.replace("\\", "/"))
    if normalized in {"", "."}:
        raise ValueError("path must not be empty")
    if normalized.startswith("/") or normalized.startswith("../") or normalized == "..":
        raise ValueError(f"path escapes publication root: {path}")
    parts = PurePosixPath(normalized).parts
    if any(part == ".." for part in parts):
        raise ValueError(f"path escapes publication root: {path}")
    return normalized


def safe_relative_path(path: str) -> str:
    """Normalize a publication-internal path and reject traversal."""

    return _normalize_relative_path(path)


def resolve_relative_path(base_path: str, href: str) -> str:
    """Resolve an href against a publication-internal base path."""

    candidate = unquote(href.split("#", 1)[0].split("?", 1)[0])
    if not candidate:
        return safe_relative_path(base_path)
    base_dir = posixpath.dirname(safe_relative_path(base_path))
    return safe_relative_path(posixpath.join(base_dir, candidate))


@dataclass(frozen=True)
class ZipPublicationSource:
    root: Path
    kind: str = "zip"

    def entries(self) -> list[SourceEntry]:
        with zipfile.ZipFile(self.root) as archive:
            return [
                SourceEntry(
                    path=safe_relative_path(info.filename),
                    size_bytes=info.file_size,
                    compressed_size_bytes=info.compress_size,
                    compress_type=info.compress_type,
                )
                for info in archive.infolist()
                if not info.is_dir()
            ]

    def exists(self, path: str) -> bool:
        target = safe_relative_path(path)
        with zipfile.ZipFile(self.root) as archive:
            try:
                archive.getinfo(target)
            except KeyError:
                return False
        return True

    def read_bytes(self, path: str) -> bytes:
        target = safe_relative_path(path)
        with zipfile.ZipFile(self.root) as archive:
            return archive.read(target)

    def read_text(self, path: str, encoding: str = "utf-8") -> str:
        return self.read_bytes(path).decode(encoding)


@dataclass(frozen=True)
class DirectoryPublicationSource:
    root: Path
    kind: str = "directory"

    def entries(self) -> list[SourceEntry]:
        entries: list[SourceEntry] = []
        for candidate in sorted(self.root.rglob("*")):
            if not candidate.is_file():
                continue
            entries.append(
                SourceEntry(
                    path=candidate.relative_to(self.root).as_posix(),
                    size_bytes=candidate.stat().st_size,
                    compressed_size_bytes=None,
                    compress_type=None,
                )
            )
        return entries

    def exists(self, path: str) -> bool:
        target = self._resolve_filesystem_path(path)
        return target.is_file()

    def read_bytes(self, path: str) -> bytes:
        return self._resolve_filesystem_path(path).read_bytes()

    def read_text(self, path: str, encoding: str = "utf-8") -> str:
        return self._resolve_filesystem_path(path).read_text(encoding=encoding)

    def _resolve_filesystem_path(self, path: str) -> Path:
        target = self.root / safe_relative_path(path)
        resolved = target.resolve()
        if resolved != self.root.resolve() and self.root.resolve() not in resolved.parents:
            raise ValueError(f"path escapes publication root: {path}")
        return resolved


def open_publication_source(path: str | Path) -> PublicationSource:
    source_path = Path(path)
    if source_path.is_dir():
        return DirectoryPublicationSource(source_path)
    return ZipPublicationSource(source_path)
