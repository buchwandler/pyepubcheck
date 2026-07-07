# Inspection

`pyepubcheck` includes a read-only inspection layer for EPUB publications.

Use it when you want more than pass/fail validation output:

```bash
pyepubcheck inspect book.epub
pyepubcheck images book.epub
pyepubcheck metadata book.epub --format json
pyepubcheck manifest book.epub --format csv
pyepubcheck nav book.epub
pyepubcheck stats book.epub --estimate-pages
```

## What inspection reports

- Container facts such as rootfiles and archive entry totals.
- Package metadata such as title, language, identifiers, and rendition layout.
- Manifest assets and whether declared files exist in the container.
- Image assets with media type, byte size, dimensions where supported, manifest properties, and reference locations.
- Navigation data from EPUB 3 navigation documents and EPUB 2 NCX files.
- Estimated word and character counts from linear spine XHTML documents.

## Read-only behavior

Inspection commands do not rewrite the EPUB and do not extract packaged EPUBs to disk for inspection.

## Page counts

`stats` and `inspect` only calculate estimated pages when `--estimate-pages` is supplied. Real page-list counts are reported from EPUB navigation when present.

## Output formats

- `inspect`: `text`, `json`, `markdown`
- `images`: `text`, `json`, `csv`, `markdown`
- `metadata`: `text`, `json`, `markdown`
- `manifest`: `text`, `json`, `csv`, `markdown`
- `nav`: `text`, `json`, `markdown`
- `stats`: `text`, `json`, `markdown`

## Python API

The public inspection API lives under `pyepubcheck.inspect`:

```python
from pyepubcheck.inspect import inspect_path

report = inspect_path("book.epub")
print(report.packages[0].title)
for image in report.images:
    print(image.path, image.format, image.width, image.height)
```
