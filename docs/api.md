# Python API

The main public API is `validate_path`.

```python
from pyepubcheck.api import validate_path
from pyepubcheck.config import ValidationConfig

report = validate_path(
    "book.epub",
    config=ValidationConfig(profile="accessibility"),
)
```

## `validate_path`

```python
validate_path(path: str | pathlib.Path, *, config: ValidationConfig | None = None) -> ValidationReport
```

`validate_path` validates one input path and returns a `ValidationReport`. The input can be a packaged EPUB archive, an expanded EPUB directory, an OPF file, or an individual content/resource file covered by the current validators. In this alpha release, packaged `.epub` inputs are primarily checked at the archive/OCF layer; expanded directories enable the broader package and content-document checks.

## Validation configuration

```python
from pyepubcheck.config import ValidationConfig

config = ValidationConfig(
    mode="auto",
    epub_version="3.0",
    profile="default",
    fail_on_warnings=False,
)
```

Important fields:

| Field              | Default     | Purpose                                                                |
| ------------------ | ----------- | ---------------------------------------------------------------------- |
| `input_path`       | `None`      | Optional input path stored in the config.                              |
| `mode`             | `"auto"`    | Validation mode: `auto`, `opf`, `xhtml`, `svg`, `nav`, `mo`, or `exp`. |
| `epub_version`     | `"3.0"`     | EPUB version string included in reports.                               |
| `profile`          | `"default"` | Validation profile.                                                    |
| `quiet`            | `False`     | CLI output flag.                                                       |
| `fail_on_warnings` | `False`     | CLI/report exit-code policy.                                           |
| `locale`           | `None`      | Locale selector where translations are implemented.                    |
| `custom_messages`  | `None`      | Custom message override file path.                                     |

## Report model

```python
from pyepubcheck.result import ValidationReport
```

A `ValidationReport` contains:

- `input_path`
- `version`
- `profile`
- `messages`
- `items`
- `metadata`

Useful methods:

```python
report.has_message("OPF-003")
report.count_message("OPF-003")
report.exit_code(fail_on_warnings=True)
```

## Result messages

Each message is a `ResultMessage`:

```python
for message in report.messages:
    print(message.id, message.severity.value, message.path, message.message)
```

Fields:

- `id`
- `severity`
- `message`
- `suggestion`
- `path`
- `line`
- `column`
- `element_id`
- `spec_ref`

## Severity values

```python
from pyepubcheck.severity import Severity

Severity.FATAL
Severity.ERROR
Severity.WARNING
Severity.INFO
Severity.USAGE
```

## Example: fail on errors or warnings

```python
from pyepubcheck.api import validate_path

report = validate_path("book.epub")
raise SystemExit(report.exit_code(fail_on_warnings=True))
```

## Example: collect warning IDs

```python
from pyepubcheck.api import validate_path
from pyepubcheck.severity import Severity

report = validate_path("book.epub")
warning_ids = sorted({m.id for m in report.messages if m.severity is Severity.WARNING})
print(warning_ids)
```
