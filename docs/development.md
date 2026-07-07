# Development

## Environment setup

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev,docs]"
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e ".[dev,docs]"
```

## Run tests

```bash
python -m pytest -q
```

Run a specific test cluster:

```bash
python -m pytest tests/acceptance/test_cli.py -q
python -m pytest tests/unit/test_opf_parser.py -q
```

## Lint and format

```bash
ruff check .
ruff format .
```

## Documentation

Docs are Markdown files in `docs/` and are rendered by Sphinx with MyST Parser.

```bash
python -m pip install -e ".[docs]"
sphinx-build -b html docs docs/_build/html
```

## Flat-layout rule

Do not move the package into `src/`. The intended import package is:

```text
pyepubcheck/
```

The setuptools package discovery configuration uses:

```toml
[tool.setuptools.packages.find]
where = ["."]
include = ["pyepubcheck*"]
```

## Adding a validation rule

1. Find or add the relevant Gherkin scenario under `specs/behavior/features`.
2. Add a mapped acceptance test.
3. Implement the check in the appropriate `pyepubcheck.checks` module.
4. Add or update unit tests for parser/check edge cases.
5. Ensure the message ID and severity match the expected behavior.
6. Run pytest and SpecMason checks.
