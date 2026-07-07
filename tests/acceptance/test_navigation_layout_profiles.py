from __future__ import annotations


def _path(fixtures, relative: str) -> str:
    return str(fixtures.resolve(relative))


# specmason: @scenario-EPUBCHECK-39AF832B
def test_navigation_toc_missing_reports_rsc_005(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck(
        _path(
            fixtures, "/epub3/07-navigation-document/files/nav-toc-missing-error.xhtml"
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-CFF9E70D
def test_layout_unknown_value_reports_rsc_005(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/08-layout/files/rendition-layout-global-unknown-value-error.opf",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-B99E6E0C
def test_media_overlay_metadata_syntax_reports_rsc_005(
    run_pyepubcheck, fixtures
) -> None:
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/09-media-overlays/files/metadata-syntax-invalid-error.smil",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-DA85124D
def test_vocab_undeclared_prefix_reports_opf_028(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck(
        _path(fixtures, "/epub3/D-vocabularies/files/prefix-undeclared-error.xhtml"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("OPF-028")


# specmason: @scenario-EPUBCHECK-BC891242
def test_edupub_missing_pagelist_reports_nav_003(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck(
        "--profile",
        "edupub",
        _path(fixtures, "/epub-edupub/files/epub/edupub-pagelist-missing-error"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("NAV-003")


# specmason: @scenario-EPUBCHECK-FD206C7E
def test_index_missing_index_reports_rsc_005(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck(
        "--profile",
        "idx",
        _path(fixtures, "/epub-indexes/files/epub/index-whole-pub-no-index-error"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-6AD8D565
def test_preview_missing_dc_type_reports_rsc_005(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck(
        "--profile",
        "preview",
        _path(fixtures, "/epub-previews/files/epub/preview-pub-dc-type-missing-error"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-C4F5841B
def test_dictionary_missing_type_reports_rsc_005_and_opf_079(
    run_pyepubcheck, fixtures
) -> None:
    result = run_pyepubcheck(
        "--profile",
        "dict",
        _path(
            fixtures, "/epub-dictionaries/files/epub/dictionary-dc-type-missing-error"
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")
    assert result.has_warning("OPF-079")


# specmason: @scenario-EPUBCHECK-FFB6D1D2
def test_region_nav_not_xhtml_reports_opf_012(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck(
        _path(fixtures, "/epub-region-nav/files/epub/data-nav-not-xhtml-error"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("OPF-012")


# specmason: @scenario-EPUBCHECK-1C965A67
def test_scriptable_component_missing_prefix_reports_opf_028(
    run_pyepubcheck, fixtures
) -> None:
    result = run_pyepubcheck(
        "--mode",
        "opf",
        _path(
            fixtures,
            "/epub-scriptable-components/files/package-document/sc-prefix-declaration-missing-error.opf",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("OPF-028")


# specmason: @scenario-EPUBCHECK-D659EDC5
def test_distributable_object_missing_identifier_reports_rsc_005(
    run_pyepubcheck, fixtures
) -> None:
    result = run_pyepubcheck(
        "--mode",
        "opf",
        _path(
            fixtures,
            "/epub-distributable-objects/files/package-document/do-collection-metadata-identifier-missing-error.opf",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-61134806
def test_accessibility_unknown_property_reports_opf_027(
    run_pyepubcheck, fixtures
) -> None:
    result = run_pyepubcheck(
        "--mode",
        "opf",
        _path(
            fixtures,
            "/epub-accessibility/files/property-prefix-a11y-unknown-value-error.opf",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.count("OPF-027") == 2


# specmason: @scenario-EPUBCHECK-8F6E9DE8
def test_localized_schema_messages_switch_language(run_pyepubcheck, fixtures) -> None:
    target = _path(fixtures, "/localization/files/schema-error")
    english = run_pyepubcheck(target, transport="subprocess")
    french = run_pyepubcheck(target, "--locale", "fr-FR", transport="subprocess")
    assert english.returncode == 1
    assert french.returncode == 1
    assert "Error tag" in english.stderr
    assert "Erreur balise" in french.stderr


# specmason: @scenario-EPUBCHECK-5539DC2D
def test_localized_css_messages_switch_language(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck(
        _path(fixtures, "/localization/files/css-error"),
        "--locale",
        "fr-FR",
        transport="subprocess",
    )
    assert result.returncode == 1
    assert "erreur css" in result.stderr


# Additional navigation tests (10 scenarios)


# specmason: @scenario-EPUBCHECK-
def test_navigation_minimal_valid(run_pyepubcheck, fixtures) -> None:
    """Verify a minimal Navigation Document."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/07-navigation-document/files/minimal.xhtml",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_navigation_heading_empty_error(run_pyepubcheck, fixtures) -> None:
    """Report an empty nav heading."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/07-navigation-document/files/content-model-heading-empty-error.xhtml",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-
def test_navigation_heading_p_error(run_pyepubcheck, fixtures) -> None:
    """Report a p element used as a nav heading."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/07-navigation-document/files/content-model-heading-p-error.xhtml",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-
def test_navigation_li_label_missing_error(run_pyepubcheck, fixtures) -> None:
    """Report a missing list item label."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/07-navigation-document/files/content-model-li-label-missing-error.xhtml",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-
def test_navigation_li_label_empty_error(run_pyepubcheck, fixtures) -> None:
    """Report an empty list item label."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/07-navigation-document/files/content-model-li-label-empty-error.xhtml",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-
def test_navigation_li_label_multiple_images_valid(run_pyepubcheck, fixtures) -> None:
    """Allow multiple images in a list item label."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/07-navigation-document/files/content-model-li-label-multiple-images-valid.xhtml",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_navigation_li_leaf_no_link_error(run_pyepubcheck, fixtures) -> None:
    """Report a leaf list item with no link (just a span label)."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/07-navigation-document/files/content-model-li-leaf-with-no-link-error.xhtml",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-
def test_navigation_toc_valid(run_pyepubcheck, fixtures) -> None:
    """Verify a valid toc nav element."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/07-navigation-document/files/nav-toc-valid.xhtml",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_navigation_page_list_valid(run_pyepubcheck, fixtures) -> None:
    """Verify a valid page-list nav element."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/07-navigation-document/files/nav-page-list-valid.xhtml",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_navigation_landmarks_valid(run_pyepubcheck, fixtures) -> None:
    """Verify a valid landmarks nav element."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/07-navigation-document/files/nav-landmarks-valid.xhtml",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()
