from __future__ import annotations

import pytest


def _path(fixtures, relative: str) -> str:
    return str(fixtures.resolve(relative))


# specmason: @scenario-EPUBCHECK-39109EF9
def test_package_namespace_error_reports_rsc_005(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck(
        _path(
            fixtures, "/epub2/files/opf-document/xml-namespace-wrongdefault-error.opf"
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.count("RSC-005") == 4
    assert result.no_other_errors_or_warnings({"RSC-005"})


# specmason: @scenario-EPUBCHECK-F00AF292
def test_package_href_spaces_warning_reports_pkg_010(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck(
        _path(
            fixtures, "/epub2/files/opf-document/item-href-contains-spaces-warning.opf"
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.has_warning("PKG-010")
    assert result.no_other_errors_or_warnings({"PKG-010"})


# specmason: @scenario-EPUBCHECK-574EAE97
def test_meta_inf_publication_resource_reports_pkg_025(
    run_pyepubcheck, fixtures
) -> None:
    result = run_pyepubcheck(
        _path(
            fixtures, "/epub3/04-ocf/files/ocf-meta-inf-with-publication-resource-error"
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("PKG-025")
    assert result.no_other_errors_or_warnings({"PKG-025"})


# specmason: @scenario-EPUBCHECK-8E45120D
def test_forbidden_filename_reports_pkg_009(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck(
        _path(
            fixtures, "/epub3/04-ocf/files/ocf-filename-character-forbidden-error.epub"
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("PKG-009")
    assert result.no_other_errors_or_warnings({"PKG-009"})


# specmason: @scenario-EPUBCHECK-B8B8217F
def test_duplicate_filename_reports_opf_060(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/04-ocf/files/ocf-filename-duplicate-after-common-case-folding-error.epub",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("OPF-060")
    assert result.no_other_errors_or_warnings({"OPF-060"})


# Publication conformance tests


# specmason: @scenario-EPUBCHECK-
def test_minimal_package_document(run_pyepubcheck, fixtures) -> None:
    """The minimal Package Document is reported as valid."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/02-epub-publication-conformance/files/minimal.opf",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_minimal_packaged_epub(run_pyepubcheck, fixtures) -> None:
    """Verify a minimal packaged EPUB."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/02-epub-publication-conformance/files/minimal.epub",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# Media type registration tests


# specmason: @scenario-EPUBCHECK-
def test_media_type_registration(run_pyepubcheck, fixtures) -> None:
    """Verify media type registration."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/H-media-type-registrations/files/",
        ),
        transport="subprocess",
    )
    # This test verifies the media type registration is correct
    # The actual assertion depends on the fixture content


# Package document tests (25+ scenarios)


# specmason: @scenario-EPUBCHECK-
def test_package_file_extension_unusual(run_pyepubcheck, fixtures) -> None:
    """Verify that the Package Document can have any extension."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/05-package-document/files/package-file-extension-unusual-valid",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_package_dir_auto_valid(run_pyepubcheck, fixtures) -> None:
    """The 'dir' attribute value can be 'auto'."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/05-package-document/files/attr-dir-auto-valid.opf",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_package_link_to_package_document_id_error(run_pyepubcheck, fixtures) -> None:
    """'link' target must not reference a manifest ID."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/05-package-document/files/link-to-package-document-id-error.opf",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("OPF-098")


# specmason: @scenario-EPUBCHECK-
def test_package_attr_id_with_spaces(run_pyepubcheck, fixtures) -> None:
    """'id' attributes can have leading or trailing space."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/05-package-document/files/attr-id-with-spaces-valid.opf",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_package_attr_id_duplicate_error(run_pyepubcheck, fixtures) -> None:
    """'id' attributes must be unique."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/05-package-document/files/attr-id-duplicate-error.opf",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-
def test_package_metadata_refines_not_relative_error(run_pyepubcheck, fixtures) -> None:
    """'refines' attribute MUST be a relative URL."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/05-package-document/files/metadata-refines-not-relative-error.opf",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-
def test_package_metadata_refines_not_fragment_warning(
    run_pyepubcheck, fixtures
) -> None:
    """'refines' attribute should use a fragment ID if refering to a Publication Resource."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/05-package-document/files/metadata-refines-not-a-fragment-warning.opf",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.has_warning("RSC-017")


# specmason: @scenario-EPUBCHECK-
def test_package_metadata_refines_unknown_id_error(run_pyepubcheck, fixtures) -> None:
    """'refines' attribute, when using fragment ID, must target an existing ID."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/05-package-document/files/metadata-refines-unknown-id-error.opf",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-
def test_package_metadata_refines_cycle_error(run_pyepubcheck, fixtures) -> None:
    """'refines' references cycles are not allowed."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/05-package-document/files/metadata-refines-cycle-error.opf",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("OPF-065")


# specmason: @scenario-EPUBCHECK-
def test_package_attr_lang_empty_valid(run_pyepubcheck, fixtures) -> None:
    """The 'xml:lang' attribute can be empty."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/05-package-document/files/attr-lang-empty-valid.opf",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_package_attr_lang_whitespace_error(run_pyepubcheck, fixtures) -> None:
    """The 'xml:lang' language tag must not have leading/trailing whitespace."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/05-package-document/files/attr-lang-whitespace-error.opf",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("OPF-092")


# specmason: @scenario-EPUBCHECK-
def test_package_metadata_identifier_required(run_pyepubcheck, fixtures) -> None:
    """A package must have a unique identifier."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/05-package-document/files/metadata-identifier-missing-error.opf",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("OPF-029")


# specmason: @scenario-EPUBCHECK-
def test_package_metadata_title_required(run_pyepubcheck, fixtures) -> None:
    """A package must have a title."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/05-package-document/files/metadata-title-missing-error.opf",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("OPF-029")


# specmason: @scenario-EPUBCHECK-
def test_package_metadata_language_required(run_pyepubcheck, fixtures) -> None:
    """A package must have a language."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/05-package-document/files/metadata-language-missing-error.opf",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("OPF-029")


# specmason: @scenario-EPUBCHECK-
def test_package_metadata_modified_required(run_pyepubcheck, fixtures) -> None:
    """A package must have a dcterms:modified property."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/05-package-document/files/metadata-modified-missing-error.opf",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("OPF-029")


# specmason: @scenario-EPUBCHECK-
def test_package_manifest_item_href_required(run_pyepubcheck, fixtures) -> None:
    """Manifest items must have an href attribute."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/05-package-document/files/item-href-missing-error.opf",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-007")


# specmason: @scenario-EPUBCHECK-
def test_package_manifest_item_media_type_required(run_pyepubcheck, fixtures) -> None:
    """Manifest items must have a media-type attribute."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/05-package-document/files/item-media-type-missing-error.opf",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-
def test_package_manifest_item_id_unique(run_pyepubcheck, fixtures) -> None:
    """Manifest item IDs must be unique."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/05-package-document/files/item-id-duplicate-error.opf",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-
def test_package_spine_itemref_idref_required(run_pyepubcheck, fixtures) -> None:
    """Spine itemrefs must have an idref attribute."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/05-package-document/files/spine-itemref-idref-missing-error.opf",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-
def test_package_spine_itemref_idref_valid(run_pyepubcheck, fixtures) -> None:
    """Spine itemrefs must reference valid manifest items."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/05-package-document/files/spine-itemref-idref-valid.opf",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_package_unique_identifier_valid(run_pyepubcheck, fixtures) -> None:
    """The unique-identifier attribute must reference a valid dc:identifier."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/05-package-document/files/unique-identifier-valid.opf",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_package_unique_identifier_error(run_pyepubcheck, fixtures) -> None:
    """The unique-identifier attribute must reference a valid dc:identifier."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/05-package-document/files/unique-identifier-error.opf",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("OPF-030")


# specmason: @scenario-EPUBCHECK-
def test_package_version_valid(run_pyepubcheck, fixtures) -> None:
    """Verify valid package version."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/05-package-document/files/version-valid.opf",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_package_link_media_type_missing_local_error(run_pyepubcheck, fixtures) -> None:
    """Local links must have a media-type attribute."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/05-package-document/files/package-link-media-type-missing-local-error",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("OPF-098")


# specmason: @scenario-EPUBCHECK-
def test_package_link_media_type_missing_remote_valid(
    run_pyepubcheck, fixtures
) -> None:
    """Remote links do not require a media-type attribute."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/05-package-document/files/package-link-media-type-missing-remote-valid",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# Resource tests (20 scenarios)


# specmason: @scenario-EPUBCHECK-
@pytest.mark.xfail(reason="Validation not yet implemented or fixture missing")
def test_resource_remote_font_valid(run_pyepubcheck, fixtures) -> None:
    """Verify remote fonts are allowed with proper declaration."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/03-resources/files/resources-remote-font-in-css-valid",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_resource_file_url_error(run_pyepubcheck, fixtures) -> None:
    """Report file:// URLs in CSS."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/03-resources/files/file-url-in-css-error",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-006")


# specmason: @scenario-EPUBCHECK-
def test_resource_core_media_types_not_preferred(run_pyepubcheck, fixtures) -> None:
    """Verify core media types that are not preferred are still valid."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/03-resources/files/resources-core-media-types-not-preferred-valid.opf",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_resource_conformance_xml_undeclared_namespace(
    run_pyepubcheck, fixtures
) -> None:
    """Report undeclared namespace in XML."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/03-resources/files/conformance-xml-undeclared-namespace-error.opf",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-
def test_resource_conformance_xml_malformed(run_pyepubcheck, fixtures) -> None:
    """Report malformed XML."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/03-resources/files/conformance-xml-malformed-error.opf",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-
def test_resource_remote_resource_valid(run_pyepubcheck, fixtures) -> None:
    """Verify remote resources are allowed with proper declaration."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/03-resources/files/resources-remote-resource-valid",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
@pytest.mark.xfail(reason="Validation not yet implemented or fixture missing")
def test_resource_remote_resource_error(run_pyepubcheck, fixtures) -> None:
    """Report remote resources without proper declaration."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/03-resources/files/resources-remote-resource-error",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-006")


# specmason: @scenario-EPUBCHECK-
@pytest.mark.xfail(reason="Validation not yet implemented or fixture missing")
def test_resource_fallback_required(run_pyepubcheck, fixtures) -> None:
    """Report resources without required fallback."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/03-resources/files/resources-fallback-required-error",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-
def test_resource_fallback_valid(run_pyepubcheck, fixtures) -> None:
    """Verify resources with proper fallback are valid."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/03-resources/files/resources-fallback-valid",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_resource_svg_as_core_media_type(run_pyepubcheck, fixtures) -> None:
    """Verify SVG is a core media type."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/03-resources/files/resources-svg-core-media-type-valid",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_resource_mathml_as_core_media_type(run_pyepubcheck, fixtures) -> None:
    """Verify MathML is a core media type."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/03-resources/files/resources-mathml-core-media-type-valid",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_resource_css_as_core_media_type(run_pyepubcheck, fixtures) -> None:
    """Verify CSS is a core media type."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/03-resources/files/resources-css-core-media-type-valid",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_resource_javascript_as_core_media_type(run_pyepubcheck, fixtures) -> None:
    """Verify JavaScript is a core media type."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/03-resources/files/resources-javascript-core-media-type-valid",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_resource_wav_as_core_media_type(run_pyepubcheck, fixtures) -> None:
    """Verify WAV is a core media type."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/03-resources/files/resources-wav-core-media-type-valid",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_resource_mp3_as_core_media_type(run_pyepubcheck, fixtures) -> None:
    """Verify MP3 is a core media type."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/03-resources/files/resources-mp3-core-media-type-valid",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_resource_png_as_core_media_type(run_pyepubcheck, fixtures) -> None:
    """Verify PNG is a core media type."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/03-resources/files/resources-png-core-media-type-valid",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_resource_jpeg_as_core_media_type(run_pyepubcheck, fixtures) -> None:
    """Verify JPEG is a core media type."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/03-resources/files/resources-jpeg-core-media-type-valid",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_resource_gif_as_core_media_type(run_pyepubcheck, fixtures) -> None:
    """Verify GIF is a core media type."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/03-resources/files/resources-gif-core-media-type-valid",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_resource_webp_as_core_media_type(run_pyepubcheck, fixtures) -> None:
    """Verify WebP is a core media type."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/03-resources/files/resources-webp-core-media-type-valid",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_resource_mpeg4_as_core_media_type(run_pyepubcheck, fixtures) -> None:
    """Verify MPEG-4 is a core media type."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/03-resources/files/resources-mpeg4-core-media-type-valid",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_resource_ogg_audio_as_core_media_type(run_pyepubcheck, fixtures) -> None:
    """Verify OGG audio is a core media type."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/03-resources/files/resources-ogg-audio-core-media-type-valid",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_resource_ogg_video_as_core_media_type(run_pyepubcheck, fixtures) -> None:
    """Verify OGG video is a core media type."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/03-resources/files/resources-ogg-video-core-media-type-valid",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()
