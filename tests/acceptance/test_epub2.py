"""Acceptance tests for EPUB 2 features.

Tests cover:
- epub2/opf-publication.feature (23 scenarios)
- epub2/opf-package-document.feature
- epub2/ocf-publication.feature
- epub2/ncx-publication.feature
- epub2/ops-content-document-xhtml.feature
- epub2/ops-content-document-svg.feature
- epub2/ops-publication.feature
"""

from __future__ import annotations

from pathlib import Path


def _epub2_fixture(fixtures, name: str) -> Path:
    return fixtures.fixture_path("/epub2/files", name)


# specmason: @scenario-EPUBCHECK-F5D49F84
def test_minimal_epub2_passes(run_pyepubcheck, fixtures) -> None:
    """Verify a minimal EPUB 2.0.1 publication."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/minimal"), transport="subprocess"
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-9642D472
def test_missing_mimetype_reports_pkg_006(run_pyepubcheck, fixtures) -> None:
    """Report a missing mimetype file."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/ocf-mimetype-missing-error"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("PKG-006")


# specmason: @scenario-EPUBCHECK-39109EF9
def test_wrong_default_namespace_reports_rsc_005(run_pyepubcheck, fixtures) -> None:
    """The default namespace must be 'http://www.idpf.org/2007/opf'."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "opf-document/xml-namespace-wrongdefault-error.opf"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-F00AF292
def test_item_href_with_spaces_reports_pkg_010(run_pyepubcheck, fixtures) -> None:
    """Report a manifest item path with unencoded spaces."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "opf-document/item-href-contains-spaces-warning.opf"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.has_warning("PKG-010")


# specmason: @scenario-EPUBCHECK-E9CAE47A
def test_unique_identifier_not_found_reports_opf_030(run_pyepubcheck, fixtures) -> None:
    """The package 'unique-identifier' attribute must be a known ID."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/opf-unique-identifier-not-found-error"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("OPF-030")


# specmason: @scenario-EPUBCHECK-90B4BC91
def test_spine_toc_attribute_missing(run_pyepubcheck, fixtures) -> None:
    """When an NCX document is present, it must be identified in the 'toc' attribute of the spine."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/opf-spine-toc-attribute-missing-error"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("OPF-003")


# specmason: @scenario-EPUBCHECK-A5693E14
def test_spine_toc_must_point_to_ncx(run_pyepubcheck, fixtures) -> None:
    """The 'toc' attribute of the spine must point to an NCX document."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/opf-spine-toc-attribute-to-non-ncx-error"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-15FB0255
def test_ncx_uid_spaces_valid(run_pyepubcheck, fixtures) -> None:
    """Verify a publication featuring a legacy NCX navigation document."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/ncx-uid-spaces-valid"), transport="subprocess"
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-759F9828
def test_ncx_id_duplicate_error(run_pyepubcheck, fixtures) -> None:
    """Report validation errors in legacy NCX documents."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/ncx-id-duplicate-error"), transport="subprocess"
    )
    assert result.returncode == 1
    assert result.has_error("NCX-002")


# specmason: @scenario-EPUBCHECK-9066DD1F
def test_ncx_missing_resource_error(run_pyepubcheck, fixtures) -> None:
    """Verify an NCX which does not link to all spine items."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/ncx-missing-resource-error"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("NCX-003")


# specmason: @scenario-EPUBCHECK-3849F4F7
def test_meta_inf_unknown_files_ignored(run_pyepubcheck, fixtures) -> None:
    """Ignore unknown files in the META-INF directory."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/ocf-metainf-file-unknown-valid"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-574EAE97
def test_meta_inf_container_missing(run_pyepubcheck, fixtures) -> None:
    """Report a missing 'container.xml' file."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/ocf-metainf-container-file-missing-fatal"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("FATAL-001")


# specmason: @scenario-EPUBCHECK-135BB243
def test_resource_not_in_manifest_usage(run_pyepubcheck, fixtures) -> None:
    """Report (usage) a container resource that is not listed in the manifest."""
    result = run_pyepubcheck(
        "--mode",
        "exp",
        "-u",
        _epub2_fixture(fixtures, "epub/opf-manifest-resource-undeclared-usage"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.has_usage("OPF-003")


# specmason: @scenario-EPUBCHECK-59D1CF07
def test_hyperlinked_document_not_in_spine(run_pyepubcheck, fixtures) -> None:
    """Report when a document hyperlinked from a content document is not in the spine."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/ops-xhtml-hyperlink-to-missing-fragment-error"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-011")


# specmason: @scenario-EPUBCHECK-38EF43F0
def test_fallback_non_resolving(run_pyepubcheck, fixtures) -> None:
    """Report a manifest fallback that does not resolve to a resource in the publication."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/opf-fallback-non-resolving-error"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("OPF-040")


# specmason: @scenario-EPUBCHECK-75DC3D98
def test_manifest_item_missing(run_pyepubcheck, fixtures) -> None:
    """Report a reference to a resource that is not listed in the manifest."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/opf-manifest-item-missing-error"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-007")


# specmason: @scenario-EPUBCHECK-6D1FF74B
def test_manifest_item_resource_missing(run_pyepubcheck, fixtures) -> None:
    """Report a resource declared in the manifest but missing from the container."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/opf-manifest-item-resource-missing-error"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-001")


# specmason: @scenario-EPUBCHECK-40ED96A2
def test_manifest_item_xhtml_mediatype_html(run_pyepubcheck, fixtures) -> None:
    """Report an XHTML OPS document declared as 'text/html'."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/opf-manifest-item-xhtml-mediatype-html-warning"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.has_warning("OPF-086")


# specmason: @scenario-EPUBCHECK-3F0B9098
def test_spine_itemref_repeated(run_pyepubcheck, fixtures) -> None:
    """Two spine 'itemref' elements cannot reference the same manifest item."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/opf-spine-itemref-repeated-error"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("OPF-003")


# specmason: @scenario-EPUBCHECK-6A4D4604
def test_spine_missing(run_pyepubcheck, fixtures) -> None:
    """Report a missing spine."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/opf-spine-missing-error"), transport="subprocess"
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-266C71E2
def test_ops_xhtml_missing_namespace(run_pyepubcheck, fixtures) -> None:
    """Report the absence of a namespace declaration."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "ops-document-xhtml/html-no-namespace-error.xhtml"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-D99D4BE6
def test_ops_xhtml_custom_namespace(run_pyepubcheck, fixtures) -> None:
    """Report the use of a custom namespaced attribute."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "ops-document-xhtml/custom-ns-attr-error.xhtml"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-D8A7A736
def test_ops_svg_namespaced_extensions(run_pyepubcheck, fixtures) -> None:
    """Verify that namespaced extensions are allowed."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "ops-document-svg/namespace-extension-valid.svg"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-12830F88
def test_ops_xhtml_minimal(run_pyepubcheck, fixtures) -> None:
    """Verify a minimal OPS XHTML document."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "ops-document-xhtml/minimal.xhtml"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-1EAA8266
def test_manifest_os_files_ignored(run_pyepubcheck, fixtures) -> None:
    """Verify that operating system files (.DS_STORE, thumbs.db) are ignored."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/opf-manifest-os-files-ignore-valid"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-217EE1D5
def test_remote_object_undeclared(run_pyepubcheck, fixtures) -> None:
    """Report a reference to a remote resource from an 'object' element when the resource is not declared."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/opf-remote-object-undeclared-error"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-006")


# specmason: @scenario-EPUBCHECK-9AC8AB1B
def test_ncx_uid_mismatch(run_pyepubcheck, fixtures) -> None:
    """Report NCX UID mismatch."""
    result = run_pyepubcheck(
        "-u",
        _epub2_fixture(fixtures, "epub/ncx-uid-mismatch-error"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.has_usage("NCX-004")


# specmason: @scenario-EPUBCHECK-DB636C20
def test_ncx_link_to_non_ops(run_pyepubcheck, fixtures) -> None:
    """Report NCX link to non-OPS resource."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/ncx-link-to-non-ops-error"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("NCX-003")


# specmason: @scenario-EPUBCHECK-15FB0255
def test_ncx_label_empty_valid(run_pyepubcheck, fixtures) -> None:
    """Verify NCX with empty labels is valid."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/ncx-label-empty-valid"), transport="subprocess"
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-759F9828
def test_ncx_id_syntax_invalid(run_pyepubcheck, fixtures) -> None:
    """Report NCX with invalid ID syntax."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/ncx-id-syntax-invalid-error"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("NCX-002")


# specmason: @scenario-EPUBCHECK-F5D49F84
def test_metadata_creator_role_clr_valid(run_pyepubcheck, fixtures) -> None:
    """Verify that the 'clr' MARC code is allowed in the opf:role attribute."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/opf-metadata-creator-role-clr-valid"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-13027092
def test_package_id_spaces_valid(run_pyepubcheck, fixtures) -> None:
    """Verify that package IDs with leading/trailing spaces are allowed."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/opf-package-id-spaces-valid"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-F00AF292
def test_ocf_filename_with_space_warning(run_pyepubcheck, fixtures) -> None:
    """Report filename with space as warning."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/ocf-filename-with-space-warning"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.has_warning("PKG-010")


# specmason: @scenario-EPUBCHECK-3849F4F7
def test_ocf_metainf_container_alternative_valid(run_pyepubcheck, fixtures) -> None:
    """Verify alternative container.xml location is valid."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/ocf-metainf-container-alternative-valid"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-41347FDF
def test_ocf_metainf_container_mediatype_invalid(run_pyepubcheck, fixtures) -> None:
    """Report invalid container.xml media type."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/ocf-metainf-container-mediatype-invalid-error"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("PKG-007")


# specmason: @scenario-EPUBCHECK-B3D1F876
def test_ocf_metainf_container_multiple_opf(run_pyepubcheck, fixtures) -> None:
    """Report multiple OPF files in container."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/ocf-metainf-container-multiple-opf-error"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("PKG-001")


# specmason: @scenario-EPUBCHECK-B57E1D97
def test_ocf_metainf_container_rootfile_full_path_empty(
    run_pyepubcheck, fixtures
) -> None:
    """Report empty rootfile full-path."""
    result = run_pyepubcheck(
        _epub2_fixture(
            fixtures, "epub/ocf-metainf-container-rootfile-full-path-empty-error"
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("PKG-001")


# specmason: @scenario-EPUBCHECK-41101BA8
def test_ocf_metainf_container_rootfile_full_path_missing(
    run_pyepubcheck, fixtures
) -> None:
    """Report missing rootfile full-path."""
    result = run_pyepubcheck(
        _epub2_fixture(
            fixtures, "epub/ocf-metainf-container-rootfile-full-path-missing-error"
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("PKG-001")


# specmason: @scenario-EPUBCHECK-3849F4F7
def test_ocf_mimetype_with_spaces(run_pyepubcheck, fixtures) -> None:
    """Report mimetype file with spaces."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/ocf-mimetype-with-spaces-error"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("PKG-007")


# specmason: @scenario-EPUBCHECK-A1794483
def test_ocf_opf_missing(run_pyepubcheck, fixtures) -> None:
    """Report missing OPF file."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/ocf-opf-missing-fatal"), transport="subprocess"
    )
    assert result.returncode == 1
    assert result.has_error("FATAL-001")


# specmason: @scenario-EPUBCHECK-4392E8B4
def test_opf_guide_reference_to_image(run_pyepubcheck, fixtures) -> None:
    """Report guide reference to image."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/opf-guide-reference-to-image-error"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("OPF-089")


# specmason: @scenario-EPUBCHECK-4392E8B4
def test_opf_guide_reference_undeclared(run_pyepubcheck, fixtures) -> None:
    """Report guide reference to undeclared resource."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/opf-guide-reference-undeclared-error"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("OPF-089")


# specmason: @scenario-EPUBCHECK-3849F4F7
def test_opf_legacy_oebps12(run_pyepubcheck, fixtures) -> None:
    """Report legacy OEBPS 1.2 namespace."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/opf-legacy-oebps12-error"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.has_warning("OPF-086")


# specmason: @scenario-EPUBCHECK-3849F4F7
def test_opf_legacy_oebps12_mediatype_css(run_pyepubcheck, fixtures) -> None:
    """Report legacy OEBPS 1.2 CSS media type."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/opf-legacy-oebps12-mediatype-css-warning"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.has_warning("OPF-086")


# specmason: @scenario-EPUBCHECK-3849F4F7
def test_opf_legacy_oebps12_mediatype_html(run_pyepubcheck, fixtures) -> None:
    """Report legacy OEBPS 1.2 HTML media type."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/opf-legacy-oebps12-mediatype-html-warning"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.has_warning("OPF-086")


# specmason: @scenario-EPUBCHECK-3849F4F7
def test_opf_pagemap_error(run_pyepubcheck, fixtures) -> None:
    """Report page map error."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/opf-pagemap-error"), transport="subprocess"
    )
    assert result.returncode == 0


# specmason: @scenario-EPUBCHECK-3849F4F7
def test_opf_pagemap_ref_not_found(run_pyepubcheck, fixtures) -> None:
    """Report page map reference not found."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/opf-pagemap-ref-not-found-warning"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.has_warning("OPF-037")


# specmason: @scenario-EPUBCHECK-9E72E593
def test_opf_version_missing(run_pyepubcheck, fixtures) -> None:
    """Report missing version attribute."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/opf-version-missing-error"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("OPF-001")


# specmason: @scenario-EPUBCHECK-3849F4F7
def test_ops_dtbook_valid(run_pyepubcheck, fixtures) -> None:
    """Verify DTBook is valid."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/ops-dtbook-valid"), transport="subprocess"
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-AC473679
def test_ops_xhtml_link_to_missing_stylesheet(run_pyepubcheck, fixtures) -> None:
    """Report link to missing stylesheet."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/ops-xhtml-link-to-missing-stylesheet-error"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-007")


# specmason: @scenario-EPUBCHECK-3849F4F7
def test_ops_xhtml_script_valid(run_pyepubcheck, fixtures) -> None:
    """Verify XHTML with script is valid."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/ops-xhtml-script-valid"), transport="subprocess"
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-3849F4F7
def test_ops_xhtml_unusual_extension(run_pyepubcheck, fixtures) -> None:
    """Verify XHTML with unusual extension is valid."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "epub/ops-xhtml-unusual-extension-valid"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-3849F4F7
def test_ops_xhtml_doctype_unresolved_entity(run_pyepubcheck, fixtures) -> None:
    """Report unresolved entity in doctype."""
    result = run_pyepubcheck(
        _epub2_fixture(
            fixtures, "ops-document-xhtml/doctype-unresolved-entity-error.xhtml"
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-495E8833
def test_ops_xhtml_doctype_html5(run_pyepubcheck, fixtures) -> None:
    """Report HTML5 doctype in EPUB 2."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "ops-document-xhtml/doctype-html5-error.xhtml"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-3016BF3D
def test_ops_xhtml_hyperlinks_nested(run_pyepubcheck, fixtures) -> None:
    """Report nested hyperlinks."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "ops-document-xhtml/hyperlinks-nested-error.xhtml"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-96AF32AB
def test_ops_xhtml_id_duplicate(run_pyepubcheck, fixtures) -> None:
    """Report duplicate ID."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "ops-document-xhtml/id-duplicate-error.xhtml"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-3849F4F7
def test_ops_xhtml_entities_unknown(run_pyepubcheck, fixtures) -> None:
    """Report unknown entities."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "ops-document-xhtml/entities-unknown-error.xhtml"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-577526DE
def test_ops_xhtml_html5_elements(run_pyepubcheck, fixtures) -> None:
    """Report HTML5 elements in EPUB 2."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "ops-document-xhtml/html5-elements-error.xhtml"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-3849F4F7
def test_ops_xhtml_svg_foreignObject_with_html(run_pyepubcheck, fixtures) -> None:
    """Verify SVG foreignObject with HTML is valid."""
    result = run_pyepubcheck(
        _epub2_fixture(
            fixtures, "ops-document-xhtml/svg-foreignObject-with-html-valid.xhtml"
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-3849F4F7
def test_ops_xhtml_svg_foreignObject_switch(run_pyepubcheck, fixtures) -> None:
    """Verify SVG foreignObject switch is valid."""
    result = run_pyepubcheck(
        _epub2_fixture(
            fixtures, "ops-document-xhtml/svg-foreignObject-switch-valid.xhtml"
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-3849F4F7
def test_ops_xhtml_class_empty(run_pyepubcheck, fixtures) -> None:
    """Verify empty class attribute is valid."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "ops-document-xhtml/class-empty-valid.xhtml"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-3849F4F7
def test_ops_xhtml_lang_attr(run_pyepubcheck, fixtures) -> None:
    """Verify language attribute is valid."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "ops-document-xhtml/lang-attr-valid.xhtml"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-3849F4F7
def test_ops_xhtml_entities_character_references(run_pyepubcheck, fixtures) -> None:
    """Verify character references are valid."""
    result = run_pyepubcheck(
        _epub2_fixture(
            fixtures, "ops-document-xhtml/entities-character-references-valid.xhtml"
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-3849F4F7
def test_ops_xhtml_edit_attributes(run_pyepubcheck, fixtures) -> None:
    """Verify edit attributes are valid."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "ops-document-xhtml/edit-attributes-valid.xhtml"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-3849F4F7
def test_ops_xhtml_edit_block_content(run_pyepubcheck, fixtures) -> None:
    """Verify edit block content is valid."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "ops-document-xhtml/edit-block-content-valid.xhtml"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-3849F4F7
def test_ops_xhtml_map_usemap_fragment(run_pyepubcheck, fixtures) -> None:
    """Verify map usemap fragment is valid."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "ops-document-xhtml/map-usemap-fragment-valid.xhtml"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-3AAD4195
def test_ops_xhtml_doctype_public_id(run_pyepubcheck, fixtures) -> None:
    """Report invalid public ID in doctype."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "ops-document-xhtml/doctype-public-id-error.xhtml"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-3849F4F7
def test_ops_svg_font_face_src(run_pyepubcheck, fixtures) -> None:
    """Verify SVG font-face src is valid."""
    result = run_pyepubcheck(
        _epub2_fixture(fixtures, "ops-document-svg/font-face-src-valid.svg"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()
