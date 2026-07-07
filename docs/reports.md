# Reports

`pyepubcheck` can render validation output to the console or to structured report files.

## Console report

The console report prints:

1. A version header.
2. Visible validation messages.
3. A success message if no selected messages are visible.
4. A compact publication summary on clean validation runs unless `--quiet`, `--no-summary`, or structured stdout is used.

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

## Inspection output

The inspection commands render read-only publication information instead of validation messages.

### Full inspection JSON

Use:

```bash
pyepubcheck inspect book.epub --format json
```

The JSON schema includes:

| Key          | Description                                                         |
| ------------ | ------------------------------------------------------------------- |
| `inputPath`  | Input publication path.                                             |
| `container`  | Container type, mimetype, rootfiles, and aggregate entry counts.    |
| `packages`   | Package-level title, version, language, spine, and identifier data. |
| `metadata`   | OPF metadata and package attributes.                                |
| `manifest`   | Manifest items and resolved resource information.                   |
| `images`     | Image inventory, dimensions, sizes, properties, and references.     |
| `navigation` | TOC, landmark, and page-list entries.                               |
| `stats`      | Estimated words, characters, and optional estimated pages.          |
| `warnings`   | Non-fatal inspection warnings.                                      |

### CSV inspection output

Use:

```bash
pyepubcheck images book.epub --format csv
pyepubcheck manifest book.epub --format csv
```

These CSV outputs are intended for scripting and tabular review.

## Writing a report to stdout

Pass `-` as the target:

```bash
pyepubcheck book.epub --json -
```

When a structured report is written to stdout, the console report is not printed unless another destination is selected in future versions.
