# SpecMason workflow

`pyepubcheck` uses SpecMason to connect the Gherkin behavior corpus to pytest coverage.

## Configuration

SpecMason is configured in `specmason.toml`.

Key paths:

| Setting       | Path                           |
| ------------- | ------------------------------ |
| Behavior root | `specs/behavior`               |
| Feature files | `specs/behavior/features`      |
| Manifest      | `specs/behavior/manifest.json` |
| Mappings      | `specs/behavior/mappings`      |
| Evidence      | `specs/behavior/evidence`      |
| Tests         | `tests`                        |

## Inspect the corpus

```bash
specmason corpus inspect --config specmason.toml --json
```

## Check mappings

```bash
specmason check --json
```

## Review coverage

```bash
specmason coverage --json --show gaps
specmason coverage --json --view tests
specmason review
```

## Mapping tests

Add a SpecMason comment above each mapped test:

```python
# specmason: @scenario-EPUBCHECK-XXXX
def test_validates_the_scenario(run_pyepubcheck, fixtures) -> None:
    result = run_pyepubcheck(...)
    assert result.returncode == 0
```

For tests that intentionally cover internal behavior rather than a Gherkin scenario, add a waiver to `specs/behavior/mappings/intentional-unmapped.json`.

## Expected pre-release checks

```bash
python -m pytest -q
specmason check --json
specmason coverage --json --show gaps
```
