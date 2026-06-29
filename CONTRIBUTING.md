# Contributing to pyepubcheck

## SpecMason Mapping Conventions

This project uses [SpecMason](https://github.com/earendil-works/specmason) to track behavior specification coverage. Every pytest test must be mapped to a Gherkin scenario or explicitly waived.

### Mapping Comments

Add a `specmason` comment before each test function or test class:

```python
# specmason: @scenario-EPUBCHECK-XXXX
def test_my_feature(run_pyepubcheck, fixtures) -> None:
    """Scenario: Verify feature X."""
    result = run_pyepubcheck(...)
    assert result.returncode == 0
```

For classes, add the comment before the class definition:

```python
# specmason: @scenario-EPUBCHECK-XXXX
class TestMyFeature:
    """Tests for feature X."""

    def test_case_1(self) -> None:
        pass
```

### Multiple Scenario Mappings

When a test covers multiple scenarios, list them all:

```python
# specmason: @scenario-EPUBCHECK-XXXX @scenario-EPUBCHECK-YYYY
def test_multiple_scenarios(run_pyepubcheck, fixtures) -> None:
    pass
```

### Waiving Internal Tests

Tests that are purely internal (test infrastructure, models, etc.) should be added to `specs/behavior/mappings/intentional-unmapped.json`:

```json
{
  "test_my_internal_test": "reason for waiving this test"
}
```

### Finding Scenario IDs

Scenario IDs are in `specs/behavior/manifest.json`. Use the following to find IDs:

```bash
# List all scenarios for a feature area
python3 -c "
import json
with open('specs/behavior/manifest.json') as f:
    manifest = json.load(f)
for item in manifest['items']:
    if 'epub3' in item['feature']:
        print(f'{item[\"id\"]}: {item[\"scenario\"][:80]}')
"

# Search for a specific scenario
python3 -c "
import json
with open('specs/behavior/manifest.json') as f:
    manifest = json.load(f)
for item in manifest['items']:
    if 'minimal' in item['scenario'].lower():
        print(f'{item[\"id\"]}: {item[\"scenario\"]}')
"
```

### Validating Mappings

Run SpecMason to check coverage:

```bash
# Check for specmason findings
specmason check --json

# View coverage gaps
specmason coverage --json --show gaps

# View reverse coverage (tests -> scenarios)
specmason coverage --json --view tests

# Generate full review report
specmason review
```

### Expected Coverage Targets

- Unmapped tests: < 20
- All acceptance tests: mapped to scenarios
- All unit tests: mapped to scenarios or waived in intentional-unmapped.json
- Infrastructure tests: waived in intentional-unmapped.json

### Test File Organization

- `tests/acceptance/` - Acceptance tests that run pyepubcheck as a black box
- `tests/unit/` - Unit tests that test individual modules
- Each acceptance test file should map to a feature area:
  - `test_epub2.py` - EPUB 2 features
  - `test_epub3.py` - EPUB 3 features
  - `test_cli.py` - CLI features
  - `test_localization.py` - Localization features
  - `test_epub_profiles.py` - Profile features (dictionaries, edupub, indexes, previews, accessibility, etc.)

### Writing New Tests

1. Find the Gherkin scenario in `specs/behavior/features/`
2. Get the scenario ID from `specs/behavior/manifest.json`
3. Create the test function with proper mapping comment
4. Add `@pytest.mark.xfail(reason="...")` if validation logic is not yet implemented
5. Run `specmason check --json` to verify no findings
6. Run `python -m pytest tests/ -q` to verify tests pass

### Pre-commit Hooks

The project uses pre-commit hooks to validate specmason mappings:

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## Code Style

- Python 3.10+
- Type annotations required
- Follow existing test patterns in `tests/`
- Use `pathlib.Path` for paths
- Keep tests focused and readable

## Running Tests

```bash
# Run all tests
python -m pytest -q

# Run specific test file
python -m pytest tests/acceptance/test_epub2.py -q

# Run with verbose output
python -m pytest tests/acceptance/test_epub2.py -v

# Run only passing tests (skip xfail)
python -m pytest tests/acceptance/test_epub2.py -v --runxfail
```

## Coverage Validation

Before submitting a PR:

1. Run `specmason check --json` - should return `{"has_errors": false}`
2. Run `python -m pytest tests/ -q` - all tests should pass
3. Run `specmason coverage --json --show gaps` - unmapped count should be < 20
