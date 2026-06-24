from __future__ import annotations

import zipfile
from pathlib import Path

from tests.support import FixtureLocator, build_epub_from_directory


# specmason: unmapped=acceptance harness filesystem helper test; internal behavior only
def test_fixture_locator_resolves_feature_relative_paths(tmp_path: Path) -> None:
    locator = FixtureLocator(tmp_path)
    expected = (tmp_path / "epub3" / "00-minimal" / "files").resolve()
    assert locator.fixture_dir("/epub3/00-minimal/files/") == expected


# specmason: unmapped=acceptance harness archive helper test; internal behavior only
def test_build_epub_from_directory_places_mimetype_first(tmp_path: Path) -> None:
    source = tmp_path / "minimal"
    (source / "EPUB").mkdir(parents=True)
    (source / "mimetype").write_text("application/epub+zip", encoding="utf-8")
    (source / "EPUB" / "content.xhtml").write_text("<html />", encoding="utf-8")

    output = build_epub_from_directory(source)

    with zipfile.ZipFile(output) as archive:
        names = archive.namelist()
        assert names[0] == "mimetype"
        assert names[1] == "EPUB/content.xhtml"
