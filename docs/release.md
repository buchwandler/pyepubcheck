# Release process

## Pre-release verification

```bash
python -m pip install -e ".[dev,docs]"
python -m pytest -q
ruff check .
specmason check --json
sphinx-build -b html docs docs/_build/html
```

## Version update

Update the version in both places:

- `pyepubcheck/__init__.py`
- `pyproject.toml`

Update `CHANGELOG.md` and `docs/changelog.md` with the release notes.

## Build distributions

Install build tools:

```bash
python -m pip install build twine
```

Build:

```bash
rm -rf dist build *.egg-info
python -m build
python -m twine check dist/*
```

## Test the wheel locally

```bash
python -m venv /tmp/pyepubcheck-release-test
/tmp/pyepubcheck-release-test/bin/python -m pip install dist/pyepubcheck-*.whl
/tmp/pyepubcheck-release-test/bin/pyepubcheck --version
```

On Windows, create a temporary virtual environment with `py -m venv` and run the equivalent `Scripts\python.exe` and `Scripts\pyepubcheck.exe` commands.

## Publish

Publish to TestPyPI first:

```bash
python -m twine upload --repository testpypi dist/*
```

Install the TestPyPI artifact in a clean environment and run `pyepubcheck --version`.

Publish to PyPI:

```bash
python -m twine upload dist/*
```

## Post-release

- Create a Git tag for the released version.
- Confirm the PyPI page renders the Markdown README correctly.
- Confirm the documentation build is published.
- Open a follow-up milestone for the next behavior coverage target.
