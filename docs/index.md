# pyepubcheck documentation

`pyepubcheck` is a clean-room Python EPUB validation project. It is built around the Gherkin behavior corpus in `specs/behavior/features` and uses SpecMason to track behavior-to-test coverage.

The package layout is intentionally flat: the importable package is `./pyepubcheck`.

```{toctree}
:maxdepth: 2
:caption: User guide

installation
quickstart
cli
inspection
reports
api
validation-scope
```

```{toctree}
:maxdepth: 2
:caption: Project guide

specmason
development
release
changelog
```

## Project status

This is a `0.1.0` alpha package. Use it as a Python-native validation tool for the behavior covered by the current tests and SpecMason mappings. Do not treat it as a complete replacement for Java EPUBCheck until the project explicitly documents full parity.

## Core entry points

- CLI: `pyepubcheck`
- Python API: `pyepubcheck.api.validate_path`
- Validation config: `pyepubcheck.config.ValidationConfig`
- Report model: `pyepubcheck.result.ValidationReport`
- Result messages: `pyepubcheck.result.ResultMessage`

## Build the docs

```bash
python -m pip install -e ".[docs]"
sphinx-build -b html docs docs/_build/html
```
