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
