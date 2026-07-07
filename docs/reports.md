# Reports

`pyepubcheck` can render validation output to the console or to structured report files.

## Console report

The console report prints:

1. A version header.
2. Visible validation messages.
3. A success message if no selected messages are visible.

Warnings, errors, and fatal messages are written to stderr. Informational and usage messages are written to stdout when selected.

## JSON report

Use `--json`:

```bash
pyepubcheck book.epub --json report.json
```

The JSON renderer returns an object with these top-level keys:

| Key           | Description                                       |
| ------------- | ------------------------------------------------- |
| `inputPath`   | Input path that was validated.                    |
| `version`     | EPUB version string from the validation config.   |
| `profile`     | Selected validation profile.                      |
| `title`       | Publication title stored in report metadata.      |
| `messages`    | Validation messages.                              |
| `items`       | Publication item metadata included in the report. |
| `publication` | Publication-level metadata.                       |

Message objects contain:

| Key        | Description                                      |
| ---------- | ------------------------------------------------ |
| `id`       | Message identifier, such as `OPF-003`.           |
| `severity` | `FATAL`, `ERROR`, `WARNING`, `INFO`, or `USAGE`. |
| `message`  | Human-readable message text.                     |
| `path`     | Related file path where available.               |
| `line`     | Line number where available.                     |
| `column`   | Column number where available.                   |

## XML report

Use `--out`:

```bash
pyepubcheck book.epub --out report.xml
```

The current XML renderer emits a compact report with the validation version, profile, title, and message list.

## XMP report

Use `--xmp`:

```bash
pyepubcheck book.epub --xmp report.xmp
```

The current XMP renderer is intentionally minimal in this alpha release.

## Writing a report to stdout

Pass `-` as the target:

```bash
pyepubcheck book.epub --json -
```

When a structured report is written to stdout, the console report is not printed unless another destination is selected in future versions.
