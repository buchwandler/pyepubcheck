# Installation

## Requirements

`pyepubcheck` requires Python 3.10 or newer.

Runtime dependencies are declared in `pyproject.toml`:

- `click>=8.1`
- `defusedxml>=0.7`
- `jsonpath-ng>=1.6`
- `lxml>=5`
- `tinycss2>=1.3`

## Install from PyPI

After the package is published:

```bash
python -m pip install pyepubcheck
```

## Install from a local checkout

```bash
git clone <repository-url>
cd pyepubcheck
python -m pip install -e .
```

## Install development dependencies

```bash
python -m pip install -e ".[dev,docs]"
```

The `dev` extra installs test and quality tools. The `docs` extra installs Sphinx and MyST Parser.

## Verify the install

```bash
pyepubcheck --version
python -m pyepubcheck --version
```

Expected output for this release:

```text
EPUBCheck v0.1.0
```
