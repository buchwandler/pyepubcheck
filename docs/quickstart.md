# Quick start

## Validate a packaged EPUB archive

```bash
pyepubcheck book.epub
```

The command prints a version header and any visible validation messages. If no visible problems are found, it prints a localized success message and a compact publication summary unless `--quiet` or `--no-summary` is used.

## Validate an expanded EPUB directory

```bash
pyepubcheck path/to/expanded-book/
```

An expanded EPUB directory normally contains `META-INF/container.xml` and one or more package documents.

## Validate a specific resource

```bash
pyepubcheck OPS/package.opf
pyepubcheck OPS/chapter-001.xhtml
pyepubcheck OPS/nav.xhtml --mode nav
pyepubcheck OPS/overlay.smil --mode mo
```

## Use a profile

```bash
pyepubcheck book.epub --profile accessibility
pyepubcheck book.epub --profile dict
pyepubcheck book.epub --profile edupub
pyepubcheck book.epub --profile idx
pyepubcheck book.epub --profile preview
```

## Generate reports

```bash
pyepubcheck book.epub --json report.json
pyepubcheck book.epub --out report.xml
pyepubcheck book.epub --xmp report.xmp
```

Use `-` as a report target to write that report to stdout:

```bash
pyepubcheck book.epub --json -
```

Only one structured report target can be selected at a time.

## Inspect a publication

```bash
pyepubcheck inspect book.epub
pyepubcheck inspect book.epub --format markdown --output book-inspection.md
pyepubcheck images book.epub --sort size --largest 10
pyepubcheck metadata book.epub --format json
pyepubcheck stats book.epub --estimate-pages
```

Inspection commands are read-only. They summarize publication contents, metadata, images, navigation, and text statistics without modifying the EPUB.

## Exit codes

- `0`: no visible fatal or error messages were produced.
- `1`: a visible fatal or error message was produced.
- `1` with `--failonwarnings`: a visible warning was produced.

## Typical CI command

```bash
pyepubcheck book.epub --json pyepubcheck-report.json --failonwarnings
```
