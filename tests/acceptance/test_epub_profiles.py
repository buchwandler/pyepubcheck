"""Acceptance tests for EPUB profile features.

Tests cover:
- epub-dictionaries (34 scenarios)
- epub-edupub (32 scenarios)
- epub-indexes (18 scenarios)
- epub-previews (10 scenarios)
- epub-accessibility (4 scenarios)
- epub-distributable-objects (2 scenarios)
- epub-scriptable-components (2 scenarios)
"""

from __future__ import annotations

from pathlib import Path

import pytest


def _profile_fixture(fixtures, profile: str, name: str) -> Path:
    return fixtures.fixture_path(f"/{profile}/files", name)


# =============================================================================
# Dictionary Profile Tests
# =============================================================================


# specmason: @scenario-EPUBCHECK-C4F5841B
def test_dictionary_dc_type_required(run_pyepubcheck, fixtures) -> None:
    """An EPUB Dictionary publication must have a 'dictionary' dc:type property."""
    result = run_pyepubcheck(
        "--profile",
        "dict",
        _profile_fixture(
            fixtures, "epub-dictionaries", "epub/dictionary-dc-type-missing-error"
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-01043CA9
def test_dictionary_single_valid(run_pyepubcheck, fixtures) -> None:
    """A publication with single EPUB Dictionary is valid."""
    result = run_pyepubcheck(
        "--profile",
        "dict",
        _profile_fixture(fixtures, "epub-dictionaries", "epub/dictionary-single-valid"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-5B3D5A1A
@pytest.mark.xfail(reason="Profile validation not yet implemented or fixture missing")
def test_dictionary_search_key_map_required(run_pyepubcheck, fixtures) -> None:
    """A single EPUB Dictionary must declare a search key map."""
    result = run_pyepubcheck(
        "--profile",
        "dict",
        _profile_fixture(
            fixtures,
            "epub-dictionaries",
            "epub/dictionary-search-key-map-missing-error",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-47B43F0E
@pytest.mark.xfail(reason="Profile validation not yet implemented or fixture missing")
def test_dictionary_type_monolingual_valid(run_pyepubcheck, fixtures) -> None:
    """A dictionary-type property 'monolingual' is valid."""
    result = run_pyepubcheck(
        "--profile",
        "dict",
        _profile_fixture(
            fixtures, "epub-dictionaries", "epub/dictionary-type-monolingual-valid"
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-3BA53D73
@pytest.mark.xfail(reason="Profile validation not yet implemented or fixture missing")
def test_dictionary_type_unknown_value(run_pyepubcheck, fixtures) -> None:
    """A dictionary-type property with an unknown value is reported."""
    result = run_pyepubcheck(
        "--profile",
        "dict",
        _profile_fixture(
            fixtures, "epub-dictionaries", "epub/dictionary-type-unknown-value-error"
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-D22648A6
@pytest.mark.xfail(reason="Profile validation not yet implemented or fixture missing")
def test_dictionary_source_language_required(run_pyepubcheck, fixtures) -> None:
    """The source language of a single-dictionary publication must be defined."""
    result = run_pyepubcheck(
        "--profile",
        "dict",
        _profile_fixture(
            fixtures,
            "epub-dictionaries",
            "epub/dictionary-source-language-missing-error",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-7571C3E2
def test_dictionary_single_publication(run_pyepubcheck, fixtures) -> None:
    """Verify a publication with a single dictionary."""
    result = run_pyepubcheck(
        "--profile",
        "dict",
        _profile_fixture(fixtures, "epub-dictionaries", "epub/dictionary-single-valid"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-4E4337DC
def test_dictionary_multiple_publication(run_pyepubcheck, fixtures) -> None:
    """Verify a publication with multiple dictionaries."""
    result = run_pyepubcheck(
        "--profile",
        "dict",
        _profile_fixture(
            fixtures, "epub-dictionaries", "epub/dictionary-multiple-valid"
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-881D1A46
@pytest.mark.xfail(reason="Profile validation not yet implemented or fixture missing")
def test_dictionary_glossary_valid(run_pyepubcheck, fixtures) -> None:
    """Verify a publication with a single glossary."""
    result = run_pyepubcheck(
        "--profile",
        "dict",
        _profile_fixture(
            fixtures, "epub-dictionaries", "epub/dictionary-glossary-valid"
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# =============================================================================
# EduPub Profile Tests
# =============================================================================


# specmason: @scenario-EPUBCHECK-E2271C84
@pytest.mark.xfail(reason="Profile validation not yet implemented or fixture missing")
def test_edupub_minimal_valid(run_pyepubcheck, fixtures) -> None:
    """a minimal EDUPUB publication is reported as valid."""
    result = run_pyepubcheck(
        "--profile",
        "edupub",
        _profile_fixture(fixtures, "epub-edupub", "epub/edupub-minimal-valid"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-35B1BB79
@pytest.mark.xfail(reason="Profile validation not yet implemented or fixture missing")
def test_edupub_dc_type_required(run_pyepubcheck, fixtures) -> None:
    """an EDUPUB publication must declare the type 'edupub'."""
    result = run_pyepubcheck(
        "--profile",
        "edupub",
        _profile_fixture(fixtures, "epub-edupub", "epub/edupub-dc-type-missing-error"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-0BBFF0F9
@pytest.mark.xfail(reason="Profile validation not yet implemented or fixture missing")
def test_edupub_accessibility_features_required(run_pyepubcheck, fixtures) -> None:
    """an EDUPUB's accessibility features must be declared."""
    result = run_pyepubcheck(
        "--profile",
        "edupub",
        _profile_fixture(
            fixtures, "epub-edupub", "epub/edupub-accessibility-features-missing-error"
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-9D45E5AE
def test_edupub_basic_publication(run_pyepubcheck, fixtures) -> None:
    """Verify a basic edupub publication."""
    result = run_pyepubcheck(
        "--profile",
        "edupub",
        _profile_fixture(fixtures, "epub-edupub", "epub/edupub-basic-valid"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-BC891242
def test_edupub_page_list_missing(run_pyepubcheck, fixtures) -> None:
    """Report an edupub publication missing a page list."""
    result = run_pyepubcheck(
        "--profile",
        "edupub",
        _profile_fixture(fixtures, "epub-edupub", "epub/edupub-pagelist-missing-error"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("NAV-003")


# specmason: @scenario-EPUBCHECK-135DF7CC
def test_edupub_page_list_valid(run_pyepubcheck, fixtures) -> None:
    """Verify an edupub publication with a page list."""
    result = run_pyepubcheck(
        "--profile",
        "edupub",
        _profile_fixture(fixtures, "epub-edupub", "epub/edupub-pagelist-valid"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-6FEEF980
@pytest.mark.xfail(reason="Profile validation not yet implemented or fixture missing")
def test_edupub_content_document_minimal(run_pyepubcheck, fixtures) -> None:
    """Minimal Content Document."""
    result = run_pyepubcheck(
        "--profile",
        "edupub",
        _profile_fixture(
            fixtures, "epub-edupub", "edupub-content-document-xhtml/minimal.xhtml"
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-235C695A
@pytest.mark.xfail(reason="Profile validation not yet implemented or fixture missing")
def test_edupub_body_as_section(run_pyepubcheck, fixtures) -> None:
    """Verify body used as an explicit section of content."""
    result = run_pyepubcheck(
        "--profile",
        "edupub",
        _profile_fixture(
            fixtures,
            "epub-edupub",
            "edupub-content-document-xhtml/body-section-valid.xhtml",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-4C8AF668
@pytest.mark.xfail(reason="Profile validation not yet implemented or fixture missing")
def test_edupub_body_section_without_heading(run_pyepubcheck, fixtures) -> None:
    """Report body used as an explicit section without a heading."""
    result = run_pyepubcheck(
        "--profile",
        "edupub",
        _profile_fixture(
            fixtures,
            "epub-edupub",
            "edupub-content-document-xhtml/body-section-no-heading-error.xhtml",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-FBECBFE2
@pytest.mark.xfail(reason="Profile validation not yet implemented or fixture missing")
def test_edupub_heading_aria_role(run_pyepubcheck, fixtures) -> None:
    """Allow a section heading specified as ARIA heading role."""
    result = run_pyepubcheck(
        "--profile",
        "edupub",
        _profile_fixture(
            fixtures,
            "epub-edupub",
            "edupub-content-document-xhtml/heading-aria-role-valid.xhtml",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# =============================================================================
# Indexes Profile Tests
# =============================================================================


# specmason: @scenario-EPUBCHECK-BBDD13E1
@pytest.mark.xfail(reason="Profile validation not yet implemented or fixture missing")
def test_indexes_minimal_valid(run_pyepubcheck, fixtures) -> None:
    """Verify a minimal index."""
    result = run_pyepubcheck(
        "--profile",
        "idx",
        _profile_fixture(fixtures, "epub-indexes", "epub/index-minimal-valid"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-9407495A
@pytest.mark.xfail(reason="Profile validation not yet implemented or fixture missing")
def test_indexes_collection_valid(run_pyepubcheck, fixtures) -> None:
    """An index collection is reported as valid."""
    result = run_pyepubcheck(
        "--profile",
        "idx",
        _profile_fixture(fixtures, "epub-indexes", "epub/index-collection-valid"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-1B7EB95D
@pytest.mark.xfail(reason="Profile validation not yet implemented or fixture missing")
def test_indexes_publication_valid(run_pyepubcheck, fixtures) -> None:
    """Verify an index publication."""
    result = run_pyepubcheck(
        "--profile",
        "idx",
        _profile_fixture(fixtures, "epub-indexes", "epub/index-publication-valid"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-FD206C7E
@pytest.mark.xfail(reason="Profile validation not yet implemented or fixture missing")
def test_indexes_publication_without_index(run_pyepubcheck, fixtures) -> None:
    """Report an index publication without an index."""
    result = run_pyepubcheck(
        "--profile",
        "idx",
        _profile_fixture(
            fixtures, "epub-indexes", "epub/index-publication-no-index-error"
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-8F665117
@pytest.mark.xfail(reason="Profile validation not yet implemented or fixture missing")
def test_indexes_single_file_valid(run_pyepubcheck, fixtures) -> None:
    """Verify a single-file index."""
    result = run_pyepubcheck(
        "--profile",
        "idx",
        _profile_fixture(fixtures, "epub-indexes", "epub/index-single-file-valid"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-5C9796E7
def test_indexes_single_file_without_index(run_pyepubcheck, fixtures) -> None:
    """Report a single-file index without an index."""
    result = run_pyepubcheck(
        "--profile",
        "idx",
        _profile_fixture(
            fixtures, "epub-indexes", "epub/index-single-file-no-index-error"
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-BF627573
@pytest.mark.xfail(reason="Profile validation not yet implemented or fixture missing")
def test_indexes_collection_valid(run_pyepubcheck, fixtures) -> None:
    """Verify an index collection."""
    result = run_pyepubcheck(
        "--profile",
        "idx",
        _profile_fixture(fixtures, "epub-indexes", "epub/index-collection-valid"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-693B30DB
def test_indexes_collection_without_index(run_pyepubcheck, fixtures) -> None:
    """Report an index collection without an index."""
    result = run_pyepubcheck(
        "--profile",
        "idx",
        _profile_fixture(
            fixtures, "epub-indexes", "epub/index-collection-no-index-error"
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# =============================================================================
# Previews Profile Tests
# =============================================================================


# specmason: @scenario-EPUBCHECK-74551862
@pytest.mark.xfail(reason="Profile validation not yet implemented or fixture missing")
def test_previews_publication_valid(run_pyepubcheck, fixtures) -> None:
    """Verify a preview publication."""
    result = run_pyepubcheck(
        "--profile",
        "preview",
        _profile_fixture(fixtures, "epub-previews", "epub/preview-publication-valid"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-6AD8D565
def test_previews_dc_type_required(run_pyepubcheck, fixtures) -> None:
    """Report a preview publication that does not identify itself in a dc:type element."""
    result = run_pyepubcheck(
        "--profile",
        "preview",
        _profile_fixture(
            fixtures, "epub-previews", "epub/preview-pub-dc-type-missing-error"
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-3272441C
@pytest.mark.xfail(reason="Profile validation not yet implemented or fixture missing")
def test_previews_source_publication_required(run_pyepubcheck, fixtures) -> None:
    """Report a preview publication that does not identify its source publication."""
    result = run_pyepubcheck(
        "--profile",
        "preview",
        _profile_fixture(
            fixtures, "epub-previews", "epub/preview-pub-source-missing-error"
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-EF5BBC17
@pytest.mark.xfail(reason="Profile validation not yet implemented or fixture missing")
def test_previews_embedded_valid(run_pyepubcheck, fixtures) -> None:
    """Verify an embedded preview."""
    result = run_pyepubcheck(
        "--profile",
        "preview",
        _profile_fixture(fixtures, "epub-previews", "epub/preview-embedded-valid"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-5EC7B933
def test_previews_embedded_manifest_required(run_pyepubcheck, fixtures) -> None:
    """Report an embedded preview that does not have a manifest."""
    result = run_pyepubcheck(
        "--profile",
        "preview",
        _profile_fixture(
            fixtures, "epub-previews", "epub/preview-embedded-no-manifest-error"
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-DD46E736
@pytest.mark.xfail(reason="Profile validation not yet implemented or fixture missing")
def test_previews_collection_valid(run_pyepubcheck, fixtures) -> None:
    """an embedded EPUB preview collection."""
    result = run_pyepubcheck(
        "--profile",
        "preview",
        _profile_fixture(fixtures, "epub-previews", "epub/preview-collection-valid"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# =============================================================================
# Accessibility Profile Tests
# =============================================================================


# specmason: @scenario-EPUBCHECK-0C05CA61
def test_accessibility_prefix_valid(run_pyepubcheck, fixtures) -> None:
    """Verify an 'a11y' prefix used in metadata properties without being declared."""
    result = run_pyepubcheck(
        "--mode",
        "opf",
        _profile_fixture(
            fixtures, "epub-accessibility", "property-prefix-a11y-valid.opf"
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-61134806
def test_accessibility_unknown_property(run_pyepubcheck, fixtures) -> None:
    """Report unknown 'a11y' metadata."""
    result = run_pyepubcheck(
        "--mode",
        "opf",
        _profile_fixture(
            fixtures,
            "epub-accessibility",
            "property-prefix-a11y-unknown-value-error.opf",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("OPF-027")


# specmason: @scenario-EPUBCHECK-086FC8AB
def test_accessibility_certifier_credential(run_pyepubcheck, fixtures) -> None:
    """Verify an 'a11y:certifierCredential' property can be defined as a link."""
    result = run_pyepubcheck(
        "--mode",
        "opf",
        _profile_fixture(
            fixtures,
            "epub-accessibility",
            "property-prefix-a11y-certifier-credential-valid.opf",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-26A3F8AE
def test_accessibility_exemption_property(run_pyepubcheck, fixtures) -> None:
    """Allow using the 'a11y:exemption' property in package metadata."""
    result = run_pyepubcheck(
        "--mode",
        "opf",
        _profile_fixture(
            fixtures, "epub-accessibility", "property-prefix-a11y-exemption-valid.opf"
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# =============================================================================
# Distributable Objects Profile Tests
# =============================================================================


# specmason: @scenario-EPUBCHECK-79CD2635
def test_distributable_object_valid(run_pyepubcheck, fixtures) -> None:
    """a simple EPUB Embedded Object."""
    result = run_pyepubcheck(
        "--mode",
        "opf",
        _profile_fixture(
            fixtures,
            "epub-distributable-objects",
            "package-document/do-collection-metadata-valid.opf",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-D659EDC5
def test_distributable_object_identifier_required(run_pyepubcheck, fixtures) -> None:
    """an embedded object must have a dc:identifier metadata."""
    result = run_pyepubcheck(
        "--mode",
        "opf",
        _profile_fixture(
            fixtures,
            "epub-distributable-objects",
            "package-document/do-collection-metadata-identifier-missing-error.opf",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# =============================================================================
# Scriptable Components Profile Tests
# =============================================================================


# specmason: @scenario-EPUBCHECK-6FA5686F
def test_scriptable_component_valid(run_pyepubcheck, fixtures) -> None:
    """A minimal embedded scriptable component is reported as valid."""
    result = run_pyepubcheck(
        "--mode",
        "opf",
        _profile_fixture(
            fixtures,
            "epub-scriptable-components",
            "package-document/sc-prefix-declaration-valid.opf",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-1C965A67
def test_scriptable_component_prefix_required(run_pyepubcheck, fixtures) -> None:
    """The 'epubsc' prefix must be declared."""
    result = run_pyepubcheck(
        "--mode",
        "opf",
        _profile_fixture(
            fixtures,
            "epub-scriptable-components",
            "package-document/sc-prefix-declaration-missing-error.opf",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("OPF-028")
