from __future__ import annotations


def _path(fixtures, relative: str) -> str:
    return str(fixtures.resolve(relative))


# specmason: @scenario-EPUBCHECK-39109EF9
def test_package_namespace_error_reports_rsc_005(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck(_path(fixtures, "/epub2/files/opf-document/xml-namespace-wrongdefault-error.opf"), transport="subprocess")
    assert result.returncode == 1
    assert result.count("RSC-005") == 4
    assert result.no_other_errors_or_warnings({"RSC-005"})


# specmason: @scenario-EPUBCHECK-F00AF292
def test_package_href_spaces_warning_reports_pkg_010(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck(_path(fixtures, "/epub2/files/opf-document/item-href-contains-spaces-warning.opf"), transport="subprocess")
    assert result.returncode == 0
    assert result.has_warning("PKG-010")
    assert result.no_other_errors_or_warnings({"PKG-010"})


# specmason: @scenario-EPUBCHECK-574EAE97
def test_meta_inf_publication_resource_reports_pkg_025(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck(_path(fixtures, "/epub3/04-ocf/files/ocf-meta-inf-with-publication-resource-error"), transport="subprocess")
    assert result.returncode == 1
    assert result.has_error("PKG-025")
    assert result.no_other_errors_or_warnings({"PKG-025"})


# specmason: @scenario-EPUBCHECK-8E45120D
def test_forbidden_filename_reports_pkg_009(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck(_path(fixtures, "/epub3/04-ocf/files/ocf-filename-character-forbidden-error.epub"), transport="subprocess")
    assert result.returncode == 1
    assert result.has_error("PKG-009")
    assert result.no_other_errors_or_warnings({"PKG-009"})


# specmason: @scenario-EPUBCHECK-B8B8217F
def test_duplicate_filename_reports_opf_060(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck(_path(fixtures, "/epub3/04-ocf/files/ocf-filename-duplicate-after-common-case-folding-error.epub"), transport="subprocess")
    assert result.returncode == 1
    assert result.has_error("OPF-060")
    assert result.no_other_errors_or_warnings({"OPF-060"})
