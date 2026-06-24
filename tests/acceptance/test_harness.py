from __future__ import annotations

from pathlib import Path

from tests.support import build_epub_from_directory


# specmason: unmapped=test infrastructure - transport smoke test
def test_in_process_transport_supports_version(run_pyepubcheck) -> None:
    result = run_pyepubcheck("--version", transport="in_process")
    assert result.returncode == 0
    assert result.stdout.strip() == "EPUBCheck v0.1.0"


# specmason: unmapped=test infrastructure - transport smoke test
def test_subprocess_transport_supports_version(run_pyepubcheck) -> None:
    result = run_pyepubcheck("--version", transport="subprocess")
    assert result.returncode == 0
    assert result.stdout.strip() == "EPUBCheck v0.1.0"


# specmason: unmapped=test infrastructure - report parsing smoke test
def test_harness_collects_json_and_xml_reports(run_pyepubcheck, tmp_path: Path) -> None:
    source = tmp_path / "sample"
    (source / "META-INF").mkdir(parents=True)
    (source / "mimetype").write_text("application/epub+zip", encoding="utf-8")
    (source / "META-INF" / "container.xml").write_text("<container />", encoding="utf-8")
    publication = build_epub_from_directory(source, tmp_path / "sample.epub")
    json_result = run_pyepubcheck(
        publication,
        "--json",
        "-",
        transport="subprocess",
    )
    xml_result = run_pyepubcheck(
        publication,
        "--out",
        "report.xml",
        transport="subprocess",
    )
    assert json_result.returncode == 0
    assert json_result.json_report is not None
    assert json_result.json_report["inputPath"].endswith("sample.epub")
    assert xml_result.returncode == 0
    assert xml_result.xml_report is not None
    assert json_result.no_other_errors_or_warnings()
    assert xml_result.no_other_errors_or_warnings()
