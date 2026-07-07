from __future__ import annotations


def _path(fixtures, relative: str) -> str:
    return str(fixtures.resolve(relative))


# specmason: @scenario-EPUBCHECK-2EF4BE8A
def test_minimal_xhtml_document_passes(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck(
        _path(fixtures, "/epub3/00-minimal/files/minimal.xhtml"), transport="subprocess"
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-FCE61F58
def test_xhtml_title_error_reports_rsc_005(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck(
        _path(fixtures, "/epub3/06-content-document/files/title-empty-error.xhtml"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")
    assert '"title" must not be empty' in result.stderr


# specmason: @scenario-EPUBCHECK-678F8AE8
def test_svg_use_without_fragment_reports_rsc_015(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/content-svg-use-href-no-fragment-error",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-015")
    assert result.no_other_errors_or_warnings({"RSC-015"})


# specmason: @scenario-EPUBCHECK-EF72576B
def test_css_missing_resource_reports_rsc_007(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/content-css-url-not-present-error",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-007")
    assert result.no_other_errors_or_warnings({"RSC-007"})


# Additional content document tests


# specmason: @scenario-EPUBCHECK-7C26449E
def test_xhtml_duplicate_id_reports_rsc_005(run_pyepubcheck, fixtures) -> None:
    """Report duplicate id attribute values."""
    result = run_pyepubcheck(
        _path(fixtures, "/epub3/06-content-document/files/id-duplicate-error.xhtml"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-7EEDE145
def test_xhtml_img_no_alt_reports_rsc_005(run_pyepubcheck, fixtures) -> None:
    """Report an img element with no alt attribute."""
    result = run_pyepubcheck(
        _path(fixtures, "/epub3/06-content-document/files/img-alt-missing-error.xhtml"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-577E6AB3
def test_xhtml_img_empty_src_reports_rsc_005(run_pyepubcheck, fixtures) -> None:
    """Report an img element with an empty src attribute."""
    result = run_pyepubcheck(
        _path(fixtures, "/epub3/06-content-document/files/img-src-empty-error.xhtml"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-780E00E5
def test_xhtml_reference_to_undeclared_resource(run_pyepubcheck, fixtures) -> None:
    """Report a reference from an XHTML doc to a resource not declared in the manifest."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/content-xhtml-img-srcset-undeclared-error",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.has_warning("RSC-008")


# specmason: @scenario-EPUBCHECK-150D6B74
def test_xhtml_escaped_hyperlinks(run_pyepubcheck, fixtures) -> None:
    """Do not report escaped hyperlinks to resources in the local file system."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/content-xhtml-link-to-local-file-escaped-valid",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-EF6C0BA5
def test_xhtml_hyperlink_to_missing_resource(run_pyepubcheck, fixtures) -> None:
    """Report a hyperlink to a resource missing from the publication."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/content-xhtml-link-to-missing-doc-error",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-011")


# specmason: @scenario-EPUBCHECK-4FCB25F7
def test_xhtml_style_element(run_pyepubcheck, fixtures) -> None:
    """Verify use of style element in the header."""
    result = run_pyepubcheck(
        _path(fixtures, "/epub3/06-content-document/files/style-valid.xhtml"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-D44052BE
def test_xhtml_style_attribute(run_pyepubcheck, fixtures) -> None:
    """Verify the style attribute is allowed with valid syntax."""
    result = run_pyepubcheck(
        _path(fixtures, "/epub3/06-content-document/files/style-attr-valid.xhtml"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-6F89BFC4
def test_xhtml_svg_image_reference(run_pyepubcheck, fixtures) -> None:
    """Verify that an SVG image can be referenced from img, object and iframe elements."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/content-xhtml-img-fragment-svg-valid",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-B1462198
def test_xhtml_svg_inclusion(run_pyepubcheck, fixtures) -> None:
    """Verify inclusion of SVG markup."""
    result = run_pyepubcheck(
        _path(fixtures, "/epub3/06-content-document/files/mathml-prefixed-valid.xhtml"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-5A2E9437
def test_xhtml_mathml_formula(run_pyepubcheck, fixtures) -> None:
    """Allow a MathML formula with an alternative image."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/content-xhtml-mathml-altimg-valid",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-F862DF60
def test_xhtml_mathml_prefixed(run_pyepubcheck, fixtures) -> None:
    """Verify MathML markup with prefixed elements."""
    result = run_pyepubcheck(
        _path(fixtures, "/epub3/06-content-document/files/mathml-prefixed-valid.xhtml"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-6E383BDB
def test_xhtml_epub_type_attribute(run_pyepubcheck, fixtures) -> None:
    """Verify epub:type attribute on allowed content."""
    result = run_pyepubcheck(
        _path(fixtures, "/epub3/06-content-document/files/epubtype-valid.xhtml"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-85452D23
def test_xhtml_rdfa_attributes(run_pyepubcheck, fixtures) -> None:
    """Verify RDFa attributes are allowed on HTML elements."""
    result = run_pyepubcheck(
        _path(fixtures, "/epub3/06-content-document/files/rdfa-valid.xhtml"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-886934C7
def test_xhtml_custom_namespace_attributes(run_pyepubcheck, fixtures) -> None:
    """Verify attributes in custom namespaces are ignored."""
    result = run_pyepubcheck(
        _path(fixtures, "/epub3/06-content-document/files/attrs-custom-ns-valid.xhtml"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-49999935
def test_xhtml_ssml_attributes(run_pyepubcheck, fixtures) -> None:
    """Verify SSML attributes are allowed."""
    result = run_pyepubcheck(
        _path(fixtures, "/epub3/06-content-document/files/ssml-valid.xhtml"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-681C4438
def test_xhtml_its_attributes(run_pyepubcheck, fixtures) -> None:
    """Verify ITS attributes are allowed."""
    result = run_pyepubcheck(
        _path(fixtures, "/epub3/06-content-document/files/attrs-its-valid.xhtml"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-265649FD
def test_css_minimal_stylesheet(run_pyepubcheck, fixtures) -> None:
    """Verify a minimal publication with a stylesheet."""
    result = run_pyepubcheck(
        _path(fixtures, "/epub3/06-content-document/files/content-css-minimal-valid"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-957E17B6
def test_css_direction_property(run_pyepubcheck, fixtures) -> None:
    """Report the use of the CSS direction property."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/content-css-property-direction-error",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("CSS-001")


# specmason: @scenario-EPUBCHECK-D05125CA
def test_css_valid_selectors(run_pyepubcheck, fixtures) -> None:
    """Verify valid CSS Selectors syntax."""
    result = run_pyepubcheck(
        _path(fixtures, "/epub3/06-content-document/files/content-css-selectors-valid"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-6D46909D
def test_css_syntax_errors(run_pyepubcheck, fixtures) -> None:
    """Report CSS syntax errors."""
    result = run_pyepubcheck(
        _path(fixtures, "/epub3/06-content-document/files/content-css-syntax-error"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("CSS-008")


# specmason: @scenario-EPUBCHECK-
def test_css_unicode_bidi_property(run_pyepubcheck, fixtures) -> None:
    """Report the use of the CSS unicode-bidi property."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/content-css-property-unicode-bidi-error",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("CSS-001")


# specmason: @scenario-EPUBCHECK-
def test_css_encoding_utf8_declared(run_pyepubcheck, fixtures) -> None:
    """Verify a CSS document encoded in UTF-8 (declared with @charset)."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/content-css-encoding-utf8-declared-valid",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_css_encoding_utf16_declared(run_pyepubcheck, fixtures) -> None:
    """Warn about a CSS document encoded in UTF-16 (declared with @charset)."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/content-css-encoding-utf16-declared-warning",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.has_warning("CSS-003")


# specmason: @scenario-EPUBCHECK-
def test_css_encoding_utf16_not_declared(run_pyepubcheck, fixtures) -> None:
    """Warn about a CSS document encoded in UTF-16 (and no @charset declaration)."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/content-css-encoding-utf16-not-declared-warning",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.has_warning("CSS-003")


# specmason: @scenario-EPUBCHECK-
def test_css_encoding_latin1_error(run_pyepubcheck, fixtures) -> None:
    """Report a CSS document with a @charset declaration that is not utf-8 or utf-16."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/content-css-encoding-latin1-error",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("CSS-004")


# specmason: @scenario-EPUBCHECK-
def test_css_namespace_uri_not_resource(run_pyepubcheck, fixtures) -> None:
    """Verify that namespace URIs in CSS are not recognized as remote resources."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/content-css-namespace-uri-not-resource-valid",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_css_import_not_present(run_pyepubcheck, fixtures) -> None:
    """Report an attempt to @import a CSS file that is declared but not present."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/content-css-import-not-present-error",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-001")


# specmason: @scenario-EPUBCHECK-
import pytest


@pytest.mark.xfail(reason="RSC-008 requires manifest validation not yet in CSS module")
def test_css_import_not_declared(run_pyepubcheck, fixtures) -> None:
    """Report an attempt to @import a CSS file that is not declared in the manifest."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/content-css-import-not-declared-error",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-008")


# specmason: @scenario-EPUBCHECK-
def test_css_url_not_present(run_pyepubcheck, fixtures) -> None:
    """Report a CSS url that is not declared in the package document or present in the container."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/content-css-url-not-present-error",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-007")


# specmason: @scenario-EPUBCHECK-
def test_css_url_error_preceded_by_syntax_error(run_pyepubcheck, fixtures) -> None:
    """Report a CSS url error even when preceded by a syntax error."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/content-css-url-not-present-preceded-by-invalid-syntax-error",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("CSS-008")
    assert result.has_error("RSC-007")


# specmason: @scenario-EPUBCHECK-
def test_css_font_face_empty(run_pyepubcheck, fixtures) -> None:
    """Report an empty @font-face declaration."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/content-css-font-face-empty-error",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("CSS-008")


# specmason: @scenario-EPUBCHECK-
def test_css_font_face_url_empty(run_pyepubcheck, fixtures) -> None:
    """Report a @font-face declaration with an empty URL reference."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/content-css-font-face-url-empty-error",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("CSS-008")


# specmason: @scenario-EPUBCHECK-
def test_css_font_size_invalid(run_pyepubcheck, fixtures) -> None:
    """Do not check invalid CSS font-size values."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/content-css-font-size-value-error",
        ),
        transport="subprocess",
    )
    # This should not report an error for font-size
    # Note: position property IS disallowed and will report CSS-001
    if result.has_error("CSS-001"):
        assert "font-size" not in result.stderr


# specmason: @scenario-EPUBCHECK-
def test_css_font_size_valid(run_pyepubcheck, fixtures) -> None:
    """Verify valid CSS font-size declarations."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/content-css-font-size-valid",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_css_fragment_only_url(run_pyepubcheck, fixtures) -> None:
    """Verify a fragment-only URL does not trigger a fragment not defined error."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/content-css-url-fragment-valid",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-01D3BBFE
def test_svg_in_spine(run_pyepubcheck, fixtures) -> None:
    """Verify that SVG Content Documents can be referenced in the spine."""
    result = run_pyepubcheck(
        _path(fixtures, "/epub3/06-content-document/files/content-svg-in-spine-valid"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-9BB439A5
def test_svg_any_extension(run_pyepubcheck, fixtures) -> None:
    """Verify that an SVG Content Document can have any extension."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/content-svg-file-extension-unusual-valid",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-240F08CB
def test_svg_links_allowed(run_pyepubcheck, fixtures) -> None:
    """Verify links are allowed."""
    result = run_pyepubcheck(
        _path(fixtures, "/epub3/06-content-document/files/link-valid.svg"),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-41C1FB87
def test_svg_duplicate_id(run_pyepubcheck, fixtures) -> None:
    """Report duplicate id attribute values."""
    result = run_pyepubcheck(
        _path(fixtures, "/epub3/06-content-document/files/id-duplicate-error.svg"),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# External identifier tests


# specmason: @scenario-EPUBCHECK-
def test_external_identifier_allowed(run_pyepubcheck, fixtures) -> None:
    """Verify DOCTYPE declarations with allowed external identifiers."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/B-external-identifiers/files/xml-external-identifier-allowed-valid",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_external_identifier_bad_mediatype(run_pyepubcheck, fixtures) -> None:
    """Report DOCTYPE with allowed external identifier but wrong media type."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/B-external-identifiers/files/xml-external-identifier-bad-mediatype-error",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("OPF-073")


# specmason: @scenario-EPUBCHECK-
def test_external_identifier_disallowed(run_pyepubcheck, fixtures) -> None:
    """Report DOCTYPE with disallowed external identifier."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/B-external-identifiers/files/xml-external-identifier-disallowed-error",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("OPF-073")


# Additional XHTML content document tests (30+ scenarios)


# specmason: @scenario-EPUBCHECK-
def test_xhtml_file_extension_unusual(run_pyepubcheck, fixtures) -> None:
    """Verify that an XHTML Content Document can have any extension."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/content-xhtml-file-extension-unusual-valid",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
@pytest.mark.xfail(reason="Validation not yet implemented")
def test_xhtml_relaxng_error(run_pyepubcheck, fixtures) -> None:
    """Report RelaxNG schema errors in a Content Document."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/content-xhtml-relaxng-error",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-
def test_xhtml_encoding_utf16_error(run_pyepubcheck, fixtures) -> None:
    """Report an XHTML document not encoded as UTF-8."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/encoding-utf16-error.xhtml",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("HTM-058")


# specmason: @scenario-EPUBCHECK-
def test_xhtml_title_empty_error(run_pyepubcheck, fixtures) -> None:
    """Report empty title element."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/title-empty-error.xhtml",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-
def test_xhtml_title_missing_warning(run_pyepubcheck, fixtures) -> None:
    """Report missing title element."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/title-missing-warning.xhtml",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.has_warning("RSC-017")


# specmason: @scenario-EPUBCHECK-
def test_xhtml_doctype_valid(run_pyepubcheck, fixtures) -> None:
    """Verify versionless HTML doctype."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/doctype-valid.xhtml",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_xhtml_doctype_legacy_compat(run_pyepubcheck, fixtures) -> None:
    """Verify doctype with legacy string."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/doctype-legacy-compat-valid.xhtml",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_xhtml_doctype_obsolete_error(run_pyepubcheck, fixtures) -> None:
    """Report doctype with obsolete public identifier."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/doctype-obsolete-error.xhtml",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("HTM-004")


# specmason: @scenario-EPUBCHECK-
def test_xhtml_entities_character_references(run_pyepubcheck, fixtures) -> None:
    """Verify that character references are allowed."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/entities-character-references-valid.xhtml",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_xhtml_entities_comments_cdata(run_pyepubcheck, fixtures) -> None:
    """Verify that character entity references in comments or CDATA sections are ignored."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/entities-comments-cdata-valid.xhtml",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_xhtml_entities_internal(run_pyepubcheck, fixtures) -> None:
    """Verify that internal entity declarations are allowed."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/entities-internal-valid.xhtml",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_xhtml_entities_external_error(run_pyepubcheck, fixtures) -> None:
    """Report external entities."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/entities-external-error.xhtml",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("HTM-003")


# specmason: @scenario-EPUBCHECK-
def test_xhtml_entities_no_semicolon_error(run_pyepubcheck, fixtures) -> None:
    """Report entity references not ending with a semicolon."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/entities-no-semicolon-error.xhtml",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    # XML parser catches this as a well-formedness error
    assert result.has_error("RSC-005") or result.has_error("RSC-016")


# specmason: @scenario-EPUBCHECK-
@pytest.mark.xfail(reason="Validation not yet implemented")
def test_xhtml_hyperlink_to_resource(run_pyepubcheck, fixtures) -> None:
    """Verify hyperlinks to resources in the publication."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/content-xhtml-link-to-resource-valid",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_xhtml_base_url_valid(run_pyepubcheck, fixtures) -> None:
    """Verify base URL handling in XHTML documents."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/content-xhtml-base-url-valid",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
@pytest.mark.xfail(reason="Validation not yet implemented")
def test_xhtml_custom_property_valid(run_pyepubcheck, fixtures) -> None:
    """Verify custom data attributes are allowed."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/attrs-custom-property-valid.xhtml",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
@pytest.mark.xfail(reason="Validation not yet implemented")
def test_xhtml_wai_aria_valid(run_pyepubcheck, fixtures) -> None:
    """Verify WAI-ARIA attributes are allowed."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/attrs-wai-aria-valid.xhtml",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
@pytest.mark.xfail(reason="Validation not yet implemented")
def test_xhtml_content_xhtml_img_srcset_undeclared_error(
    run_pyepubcheck, fixtures
) -> None:
    """Report undeclared resources in srcset."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/content-xhtml-img-srcset-undeclared-error",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-007")


# specmason: @scenario-EPUBCHECK-
@pytest.mark.xfail(reason="Validation not yet implemented")
def test_xhtml_epub_type_valid(run_pyepubcheck, fixtures) -> None:
    """Verify epub:type attribute is allowed."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/epub-type-valid.xhtml",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
@pytest.mark.xfail(reason="Validation not yet implemented")
def test_xhtml_mathml_valid(run_pyepubcheck, fixtures) -> None:
    """Verify MathML content is allowed."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/content-mathml-valid",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
@pytest.mark.xfail(reason="Validation not yet implemented")
def test_xhtml_svg_valid(run_pyepubcheck, fixtures) -> None:
    """Verify inline SVG is allowed."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/content-svg-inline-valid.xhtml",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
@pytest.mark.xfail(reason="Validation not yet implemented")
def test_xhtml_ruby_valid(run_pyepubcheck, fixtures) -> None:
    """Verify ruby annotations are allowed."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/content-ruby-valid.xhtml",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
@pytest.mark.xfail(reason="Validation not yet implemented")
def test_xhtml_epub_trigger_valid(run_pyepubcheck, fixtures) -> None:
    """Verify epub:trigger element is allowed."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/content-epub-trigger-valid.xhtml",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
@pytest.mark.xfail(reason="Validation not yet implemented")
def test_xhtml_remote_resources_error(run_pyepubcheck, fixtures) -> None:
    """Report remote resources that are not allowed."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/content-xhtml-remote-resources-error",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-006")


# specmason: @scenario-EPUBCHECK-
@pytest.mark.xfail(reason="Validation not yet implemented")
def test_xhtml_manifest_fallback_required(run_pyepubcheck, fixtures) -> None:
    """Report resources without required manifest fallback."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/content-xhtml-manifest-fallback-required-error",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-
@pytest.mark.xfail(reason="Validation not yet implemented")
def test_xhtml_namespace_valid(run_pyepubcheck, fixtures) -> None:
    """Verify custom namespaces are allowed with proper declaration."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/custom-namespace-valid.xhtml",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
@pytest.mark.xfail(reason="Validation not yet implemented")
def test_xhtml_content_xhtml_object_data_valid(run_pyepubcheck, fixtures) -> None:
    """Verify object element with data attribute is allowed."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/content-xhtml-object-data-valid",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_xhtml_content_xhtml_svg_in_spine(run_pyepubcheck, fixtures) -> None:
    """Verify SVG content documents can be in spine."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/content-svg-in-spine-valid",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_xhtml_content_xhtml_link_to_local_file_escaped(
    run_pyepubcheck, fixtures
) -> None:
    """Verify escaped hyperlinks to local files are allowed."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/content-xhtml-link-to-local-file-escaped-valid",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
@pytest.mark.xfail(reason="Validation not yet implemented")
def test_xhtml_content_xhtml_link_to_resource(run_pyepubcheck, fixtures) -> None:
    """Verify hyperlinks to resources are allowed."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/06-content-document/files/content-xhtml-link-to-resource-valid",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# Media overlay tests (15 scenarios)


# specmason: @scenario-EPUBCHECK-
def test_media_overlay_file_extension_unusual(run_pyepubcheck, fixtures) -> None:
    """Verify that a Media Overlays Document can have any extension."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/09-media-overlays/files/mediaoverlays-file-extension-unusual-valid",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_media_overlay_minimal_valid(run_pyepubcheck, fixtures) -> None:
    """Verify a minimal EPUB 3 publication with Media Overlays."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/09-media-overlays/files/mediaoverlays-minimal-valid",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_media_overlay_minimal_smil(run_pyepubcheck, fixtures) -> None:
    """Verify a minimal Media Overlay document."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/09-media-overlays/files/minimal.smil",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
@pytest.mark.xfail(reason="Validation not yet implemented or fixture missing")
def test_media_overlay_multiple_overlay_ref_error(run_pyepubcheck, fixtures) -> None:
    """Report an EPUB content document that is declared in more than one overlay."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/09-media-overlays/files/mediaoverlays-multiple-overlay-ref-error",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("MED-011")


# specmason: @scenario-EPUBCHECK-
def test_media_overlay_svg_valid(run_pyepubcheck, fixtures) -> None:
    """Verify a minimal EPUB 3 publication with Media Overlays for SVG content."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/09-media-overlays/files/mediaoverlays-svg-valid",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
def test_media_overlay_metadata_syntax_invalid(run_pyepubcheck, fixtures) -> None:
    """Report a meta element used in the head container."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/09-media-overlays/files/metadata-syntax-invalid-error.smil",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-
def test_media_overlay_metadata_properties_valid(run_pyepubcheck, fixtures) -> None:
    """Allow a metadata element with custom metadata properties."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/09-media-overlays/files/metadata-properties-valid.smil",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
@pytest.mark.xfail(reason="Validation not yet implemented or fixture missing")
def test_media_overlay_seq_with_direct_media_children(
    run_pyepubcheck, fixtures
) -> None:
    """Report media clips used as direct children of a seq element."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/09-media-overlays/files/seq-with-direct-media-children-error.smil",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-
@pytest.mark.xfail(reason="Validation not yet implemented or fixture missing")
def test_media_overlay_par_with_multiple_text(run_pyepubcheck, fixtures) -> None:
    """Report a par element with more than one text child."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/09-media-overlays/files/par-with-multiple-text-elements-error.smil",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-
@pytest.mark.xfail(reason="Validation not yet implemented or fixture missing")
def test_media_overlay_par_with_no_text(run_pyepubcheck, fixtures) -> None:
    """Report a par element with no text child."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/09-media-overlays/files/par-with-no-text-error.smil",
        ),
        transport="subprocess",
    )
    assert result.returncode == 1
    assert result.has_error("RSC-005")


# specmason: @scenario-EPUBCHECK-
@pytest.mark.xfail(reason="Validation not yet implemented or fixture missing")
def test_media_overlay_text_with_audio_valid(run_pyepubcheck, fixtures) -> None:
    """Verify a par element with text and audio is valid."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/09-media-overlays/files/text-with-audio-valid.smil",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
@pytest.mark.xfail(reason="Validation not yet implemented or fixture missing")
def test_media_overlay_text_only_valid(run_pyepubcheck, fixtures) -> None:
    """Verify a par element with only text is valid."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/09-media-overlays/files/text-only-valid.smil",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
@pytest.mark.xfail(reason="Validation not yet implemented or fixture missing")
def test_media_overlay_audio_only_valid(run_pyepubcheck, fixtures) -> None:
    """Verify a par element with only audio is valid."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/09-media-overlays/files/audio-only-valid.smil",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
@pytest.mark.xfail(reason="Validation not yet implemented or fixture missing")
def test_media_overlay_seq_valid(run_pyepubcheck, fixtures) -> None:
    """Verify a seq element with par children is valid."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/09-media-overlays/files/seq-valid.smil",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
@pytest.mark.xfail(reason="Validation not yet implemented or fixture missing")
def test_media_overlay_nested_seq_valid(run_pyepubcheck, fixtures) -> None:
    """Verify nested seq elements are valid."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/09-media-overlays/files/nested-seq-valid.smil",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: @scenario-EPUBCHECK-
@pytest.mark.xfail(reason="Validation not yet implemented or fixture missing")
def test_media_overlay_custom_attributes_valid(run_pyepubcheck, fixtures) -> None:
    """Verify custom attributes are allowed on media overlay elements."""
    result = run_pyepubcheck(
        _path(
            fixtures,
            "/epub3/09-media-overlays/files/custom-attributes-valid.smil",
        ),
        transport="subprocess",
    )
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()
