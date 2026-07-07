# pyepubcheck

`pyepubcheck` is a clean-room Python EPUB validation project driven by the imported EPUBCheck behavior specifications in `specs/behavior/features`.

The package intentionally uses a flat layout: importable code lives in `./pyepubcheck`, not in `./src`.

> Status: `0.1.0` alpha. The project is suitable for validating the behavior covered by its current test suite and SpecMason mappings. It is not yet a complete drop-in replacement for the Java EPUBCheck distribution.

## Features

- CLI command named `pyepubcheck`.
- Validation of expanded EPUB directories and individual OPF, XHTML, SVG, navigation, CSS, NCX, and media overlay resources.
- EPUB 2 and EPUB 3 behavior coverage derived from Gherkin scenarios.
- Optional profile checks for dictionaries, EDUPUB, indexes, previews, accessibility, and related profile constraints.
- Console, JSON, XML, and XMP report renderers.
- Read-only publication inspection for metadata, manifest items, images, navigation, and text statistics.
- Image inventory reports with media type, byte size, dimensions, manifest properties, and references.
- Metadata reports for OPF Dublin Core fields, rendition metadata, accessibility-related entries, and package identifiers.
- Custom message override support compatible with the project acceptance tests.
- SpecMason configuration for tracking Gherkin-to-test coverage.

## Requirements

- Python 3.10 or newer.
- Runtime dependencies declared in `pyproject.toml`:
  - `click`
  - `defusedxml`
  - `jsonpath-ng`
  - `lxml`
  - `tinycss2`

## Installation

From PyPI after publication:

```bash
python -m pip install pyepubcheck
```

From a local checkout:

```bash
git clone <repository-url>
cd pyepubcheck
python -m pip install -e .
```

For development, tests, and documentation:

```bash
python -m pip install -e ".[dev,docs]"
```

## Quick start

Validate an expanded EPUB directory:

```bash
pyepubcheck path/to/book/
```

Validate packaged EPUB archive structure or a single resource:

```bash
pyepubcheck book.epub
pyepubcheck OPS/package.opf
pyepubcheck OPS/chapter-001.xhtml
```

Inspect a publication:

```bash
pyepubcheck inspect book.epub
pyepubcheck images book.epub --sort size --largest 10
pyepubcheck metadata book.epub --format json
pyepubcheck stats book.epub --estimate-pages
```

Write a JSON report:

```bash
pyepubcheck book.epub --json report.json
```

Fail the command when warnings are present:

```bash
pyepubcheck book.epub --failonwarnings
```

Use a validation profile:

```bash
pyepubcheck book.epub --profile accessibility
pyepubcheck book.epub --profile edupub
```

## CLI reference

```text
usage: pyepubcheck [-h] [--version]
                   {check,inspect,images,metadata,manifest,nav,stats} ...
```

Legacy validation remains supported:

```bash
pyepubcheck book.epub
```

This behaves like:

```bash
pyepubcheck check book.epub
```

Primary commands:

| Command    | Purpose                                                                   |
| ---------- | ------------------------------------------------------------------------- |
| `check`    | Validate a publication and optionally append a compact clean-run summary. |
| `inspect`  | Produce an all-in-one read-only publication overview.                     |
| `images`   | List image assets, dimensions, byte sizes, properties, and references.    |
| `metadata` | Report stored OPF metadata and package identifiers.                       |
| `manifest` | Report manifest items, resolved paths, and file presence.                 |
| `nav`      | Report TOC, landmarks, and page-list data.                                |
| `stats`    | Report estimated word and character counts and optional estimated pages.  |

## Python API

```python
from pyepubcheck.api import validate_path
from pyepubcheck.config import ValidationConfig
from pyepubcheck.severity import Severity

report = validate_path(
    "book.epub",
    config=ValidationConfig(profile="accessibility", fail_on_warnings=True),
)

for message in report.messages:
    print(message.severity.value, message.id, message.message)

exit_code = report.exit_code(fail_on_warnings=True)
assert exit_code in {0, 1}
assert all(message.severity is not Severity.FATAL for message in report.messages)
```

## Documentation

The documentation is authored as Markdown under `docs/` and rendered with MyST Parser.

Build it locally:

```bash
python -m pip install -e ".[docs]"
sphinx-build -b html docs docs/_build/html
```

Start with [`docs/index.md`](docs/index.md).

## Development

```bash
python -m pip install -e ".[dev,docs]"
python -m pytest -q
ruff check .
specmason check --json
specmason coverage --json --show gaps
```

The SpecMason configuration lives in `specmason.toml`; the imported Gherkin corpus lives under `specs/behavior/features`.

## Release checklist

1. Update `pyepubcheck/__init__.py` and `pyproject.toml` to the release version.
2. Run the test suite: `python -m pytest -q`.
3. Run SpecMason checks: `specmason check --json`.
4. Build the docs: `sphinx-build -b html docs docs/_build/html`.
5. Build distributions: `python -m build`.
6. Inspect distributions: `python -m twine check dist/*`.
7. Publish to TestPyPI, install into a clean virtual environment, then publish to PyPI.

## License

MIT. See [`LICENSE`](LICENSE).

## Attribution

This project is a clean-room Python implementation guided by public EPUB behavior specifications and test scenarios. It is not affiliated with, endorsed by, or maintained by the EPUBCheck project.
