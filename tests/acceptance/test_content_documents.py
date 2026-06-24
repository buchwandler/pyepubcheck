from __future__ import annotations


def _path(fixtures, relative: str) -> str:
    return str(fixtures.resolve(relative))


# specmason: unmapped=content-document acceptance slice pending imported requirement mapping
def test_minimal_xhtml_document_passes(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck(_path(fixtures, "/epub3/00-minimal/files/minimal.xhtml"), transport="subprocess")
    assert result.returncode == 0
    assert result.no_other_errors_or_warnings()


# specmason: unmapped=content-document acceptance slice pending imported requirement mapping
def test_xhtml_title_error_reports_rsc_005(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck(_path(fixtures, "/epub3/06-content-document/files/title-empty-error.xhtml"), transport="subprocess")
    assert result.returncode == 1
    assert result.has_error("RSC-005")
    assert '"title" must not be empty' in result.stderr


# specmason: unmapped=content-document acceptance slice pending imported requirement mapping
def test_svg_use_without_fragment_reports_rsc_015(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck(_path(fixtures, "/epub3/06-content-document/files/content-svg-use-href-no-fragment-error"), transport="subprocess")
    assert result.returncode == 1
    assert result.has_error("RSC-015")
    assert result.no_other_errors_or_warnings({"RSC-015"})


# specmason: unmapped=content-document acceptance slice pending imported requirement mapping
def test_css_missing_resource_reports_rsc_007(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck(_path(fixtures, "/epub3/06-content-document/files/content-css-url-not-present-error"), transport="subprocess")
    assert result.returncode == 1
    assert result.has_error("RSC-007")
    assert result.no_other_errors_or_warnings({"RSC-007"})
