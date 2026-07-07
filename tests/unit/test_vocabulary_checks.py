"""Unit tests for vocabulary and prefix validation checks."""

from __future__ import annotations

from pathlib import Path

from pyepubcheck.checks.package import _validate_prefix_attribute


# specmason: @scenario-EPUBCHECK-
class TestPrefixAttributeSyntax:
    """Test prefix attribute syntax validation."""

    def test_valid_single_prefix(self, tmp_path: Path) -> None:
        """Allow valid single prefix mapping."""
        errors = _validate_prefix_attribute(
            tmp_path / "test.opf", "foaf: http://xmlns.com/foaf/spec/"
        )
        assert len(errors) == 0

    def test_valid_multiple_prefixes(self, tmp_path: Path) -> None:
        """Allow valid multiple prefix mappings."""
        errors = _validate_prefix_attribute(
            tmp_path / "test.opf",
            "foaf: http://xmlns.com/foaf/spec/ dcterms: http://purl.org/dc/terms/",
        )
        assert len(errors) == 0

    def test_invalid_syntax_missing_colon(self, tmp_path: Path) -> None:
        """Report syntax error when prefix is missing colon."""
        errors = _validate_prefix_attribute(
            tmp_path / "test.opf", "foaf http://xmlns.com/foaf/spec/"
        )
        assert any(e.id == "OPF-007b" for e in errors)

    def test_invalid_syntax_missing_uri(self, tmp_path: Path) -> None:
        """Report syntax error when URI is missing."""
        errors = _validate_prefix_attribute(tmp_path / "test.opf", "foaf:")
        assert any(e.id == "OPF-007b" for e in errors)

    def test_empty_prefix_attribute(self, tmp_path: Path) -> None:
        """Empty prefix attribute should not report errors."""
        errors = _validate_prefix_attribute(tmp_path / "test.opf", "")
        assert len(errors) == 0


# specmason: @scenario-EPUBCHECK-
class TestPrefixReservedVocabularies:
    """Test that default vocabularies cannot be remapped."""

    def test_a11y_prefix_allowed(self, tmp_path: Path) -> None:
        """a11y prefix is a reserved prefix and should be allowed."""
        errors = _validate_prefix_attribute(
            tmp_path / "test.opf", "a11y: http://www.idpf.org/epub/vocab/package/a11y/#"
        )
        # This should not error for the prefix attribute itself
        # (the actual validation of using a11y: in properties is separate)
        assert not any(e.id == "OPF-007b" for e in errors)

    def test_schema_prefix_allowed(self, tmp_path: Path) -> None:
        """schema prefix is a reserved prefix and should be allowed."""
        errors = _validate_prefix_attribute(
            tmp_path / "test.opf", "schema: http://schema.org/"
        )
        assert not any(e.id == "OPF-007b" for e in errors)
