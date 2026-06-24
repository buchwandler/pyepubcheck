"""Unit tests for OCF checks."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from pyepubcheck.checks.ocf import (
    EXPECTED_MIMETYPE,
    _check_duplicate_filenames,
    _check_meta_inf_resources,
    _validate_archive,
    _validate_directory,
    _validate_filename,
    _validate_mimetype_content,
    run,
)


class TestValidateMimetypeContent:
    """Test mimetype content validation."""

    def test_valid_mimetype(self) -> None:
        errors = _validate_mimetype_content("application/epub+zip")
        assert len(errors) == 0

    def test_incorrect_value(self) -> None:
        errors = _validate_mimetype_content("application/zip")
        assert len(errors) == 1
        assert errors[0].id == "PKG-007"

    def test_leading_whitespace(self) -> None:
        errors = _validate_mimetype_content(" application/epub+zip")
        assert len(errors) == 1
        assert errors[0].id == "PKG-007"

    def test_trailing_newline_tolerated(self) -> None:
        # Trailing newlines are common in valid EPUBs and tolerated
        errors = _validate_mimetype_content("application/epub+zip\n")
        assert len(errors) == 0


class TestValidateFilename:
    """Test filename validation."""

    def test_valid_filename(self) -> None:
        errors = _validate_filename("EPUB/content.xhtml")
        assert len(errors) == 0

    def test_forbidden_plus(self) -> None:
        errors = _validate_filename("file+name.xhtml")
        assert len(errors) == 1
        assert errors[0].id == "PKG-009"

    def test_forbidden_quote(self) -> None:
        errors = _validate_filename('file"name.xhtml')
        assert len(errors) == 1
        assert errors[0].id == "PKG-009"

    def test_forbidden_control_char(self) -> None:
        errors = _validate_filename("file\x01name.xhtml")
        assert len(errors) == 1
        assert errors[0].id == "PKG-009"


class TestCheckDuplicateFilenames:
    """Test duplicate filename detection."""

    def test_no_duplicates(self) -> None:
        errors = _check_duplicate_filenames(["file1.xhtml", "file2.xhtml"])
        assert len(errors) == 0

    def test_common_case_fold_duplicate(self) -> None:
        errors = _check_duplicate_filenames(["File.xhtml", "file.xhtml"])
        assert len(errors) == 1
        assert errors[0].id == "OPF-060"


class TestCheckMetaInfResources:
    """Test META-INF resource checks."""

    def test_allowed_meta_inf(self) -> None:
        errors = _check_meta_inf_resources([
            "META-INF/container.xml",
            "META-INF/encryption.xml",
        ])
        assert len(errors) == 0

    def test_forbidden_meta_inf(self) -> None:
        errors = _check_meta_inf_resources(["META-INF/image.png"])
        assert len(errors) == 1
        assert errors[0].id == "PKG-025"


class TestValidateDirectory:
    """Test directory validation."""

    def test_valid_directory(self, tmp_path: Path) -> None:
        epub_dir = tmp_path / "test"
        epub_dir.mkdir()
        (epub_dir / "mimetype").write_text("application/epub+zip")
        errors = _validate_directory(epub_dir)
        assert len(errors) == 0

    def test_missing_mimetype(self, tmp_path: Path) -> None:
        epub_dir = tmp_path / "test"
        epub_dir.mkdir()
        errors = _validate_directory(epub_dir)
        assert len(errors) == 1
        assert errors[0].id == "PKG-006"

    def test_invalid_mimetype(self, tmp_path: Path) -> None:
        epub_dir = tmp_path / "test"
        epub_dir.mkdir()
        (epub_dir / "mimetype").write_text("application/zip")
        errors = _validate_directory(epub_dir)
        assert len(errors) == 1
        assert errors[0].id == "PKG-007"


class TestValidateArchive:
    """Test archive validation."""

    def test_valid_archive(self, tmp_path: Path) -> None:
        epub_file = tmp_path / "test.epub"
        with zipfile.ZipFile(epub_file, "w") as zf:
            zf.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
            zf.writestr("EPUB/content.xhtml", "<html/>")
        errors = _validate_archive(epub_file)
        assert len(errors) == 0

    def test_missing_mimetype(self, tmp_path: Path) -> None:
        epub_file = tmp_path / "test.epub"
        with zipfile.ZipFile(epub_file, "w") as zf:
            zf.writestr("EPUB/content.xhtml", "<html/>")
        errors = _validate_archive(epub_file)
        assert len(errors) == 1
        assert errors[0].id == "PKG-006"

    def test_mimetype_not_first(self, tmp_path: Path) -> None:
        epub_file = tmp_path / "test.epub"
        with zipfile.ZipFile(epub_file, "w") as zf:
            zf.writestr("EPUB/content.xhtml", "<html/>")
            zf.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        errors = _validate_archive(epub_file)
        assert any(e.id == "PKG-005" for e in errors)

    def test_invalid_mimetype_value(self, tmp_path: Path) -> None:
        epub_file = tmp_path / "test.epub"
        with zipfile.ZipFile(epub_file, "w") as zf:
            zf.writestr("mimetype", "application/zip", compress_type=zipfile.ZIP_STORED)
        errors = _validate_archive(epub_file)
        assert any(e.id == "PKG-007" for e in errors)

    def test_forbidden_filename(self, tmp_path: Path) -> None:
        epub_file = tmp_path / "test.epub"
        with zipfile.ZipFile(epub_file, "w") as zf:
            zf.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
            zf.writestr("file+name.xhtml", "<html/>")
        errors = _validate_archive(epub_file)
        assert any(e.id == "PKG-009" for e in errors)

    def test_empty_archive(self, tmp_path: Path) -> None:
        epub_file = tmp_path / "test.epub"
        with zipfile.ZipFile(epub_file, "w"):
            pass
        errors = _validate_archive(epub_file)
        assert len(errors) == 1
        assert errors[0].id == "PKG-006"


class TestRun:
    """Test run function."""

    def test_directory(self, tmp_path: Path) -> None:
        epub_dir = tmp_path / "test"
        epub_dir.mkdir()
        (epub_dir / "mimetype").write_text("application/epub+zip")
        errors = run(epub_dir)
        assert len(errors) == 0

    def test_epub_file(self, tmp_path: Path) -> None:
        epub_file = tmp_path / "test.epub"
        with zipfile.ZipFile(epub_file, "w") as zf:
            zf.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        errors = run(epub_file)
        assert len(errors) == 0

    def test_other_file(self, tmp_path: Path) -> None:
        other_file = tmp_path / "test.txt"
        other_file.write_text("test")
        errors = run(other_file)
        assert len(errors) == 0
