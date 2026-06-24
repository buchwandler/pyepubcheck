from __future__ import annotations


def _path(fixtures, relative: str) -> str:
    return str(fixtures.resolve(relative))


# specmason: @scenario-EPUBCHECK-39AF832B
def test_navigation_toc_missing_reports_rsc_005(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck(_path(fixtures, "/epub3/07-navigation-document/files/nav-toc-missing-error.xhtml"), transport="subprocess")
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-CFF9E70D
def test_layout_unknown_value_reports_rsc_005(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck(_path(fixtures, "/epub3/08-layout/files/rendition-layout-global-unknown-value-error.opf"), transport="subprocess")
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-B99E6E0C
def test_media_overlay_metadata_syntax_reports_rsc_005(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck(_path(fixtures, "/epub3/09-media-overlays/files/metadata-syntax-invalid-error.smil"), transport="subprocess")
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-DA85124D
def test_vocab_undeclared_prefix_reports_opf_028(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck(_path(fixtures, "/epub3/D-vocabularies/files/prefix-undeclared-error.xhtml"), transport="subprocess")
    assert result.returncode == 1
    assert result.has_error("OPF-028")


# specmason: @scenario-EPUBCHECK-BC891242
def test_edupub_missing_pagelist_reports_nav_003(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck("--profile", "edupub", _path(fixtures, "/epub-edupub/files/epub/edupub-pagelist-missing-error"), transport="subprocess")
    assert result.returncode == 1
    assert result.has_error("NAV-003")


# specmason: @scenario-EPUBCHECK-FD206C7E
def test_index_missing_index_reports_rsc_005(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck("--profile", "idx", _path(fixtures, "/epub-indexes/files/epub/index-whole-pub-no-index-error"), transport="subprocess")
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-6AD8D565
def test_preview_missing_dc_type_reports_rsc_005(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck("--profile", "preview", _path(fixtures, "/epub-previews/files/epub/preview-pub-dc-type-missing-error"), transport="subprocess")
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-C4F5841B
def test_dictionary_missing_type_reports_rsc_005_and_opf_079(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck("--profile", "dict", _path(fixtures, "/epub-dictionaries/files/epub/dictionary-dc-type-missing-error"), transport="subprocess")
    assert result.returncode == 1
    assert result.has_error("RSC-005")
    assert result.has_warning("OPF-079")


# specmason: @scenario-EPUBCHECK-FFB6D1D2
def test_region_nav_not_xhtml_reports_opf_012(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck(_path(fixtures, "/epub-region-nav/files/epub/data-nav-not-xhtml-error"), transport="subprocess")
    assert result.returncode == 1
    assert result.has_error("OPF-012")


# specmason: @scenario-EPUBCHECK-1C965A67
def test_scriptable_component_missing_prefix_reports_opf_028(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck("--mode", "opf", _path(fixtures, "/epub-scriptable-components/files/package-document/sc-prefix-declaration-missing-error.opf"), transport="subprocess")
    assert result.returncode == 1
    assert result.has_error("OPF-028")


# specmason: @scenario-EPUBCHECK-D659EDC5
def test_distributable_object_missing_identifier_reports_rsc_005(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck("--mode", "opf", _path(fixtures, "/epub-distributable-objects/files/package-document/do-collection-metadata-identifier-missing-error.opf"), transport="subprocess")
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-61134806
def test_accessibility_unknown_property_reports_opf_027(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck("--mode", "opf", _path(fixtures, "/epub-accessibility/files/property-prefix-a11y-unknown-value-error.opf"), transport="subprocess")
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
    result = run_pyepubcheck(_path(fixtures, "/localization/files/css-error"), "--locale", "fr-FR", transport="subprocess")
    assert result.returncode == 1
    assert "erreur css" in result.stderr
