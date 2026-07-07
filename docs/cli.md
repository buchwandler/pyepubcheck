# Command-line interface

The console command is `pyepubcheck`.

```text
usage: pyepubcheck [-h] [--version]
                   {check,inspect,images,metadata,manifest,nav,stats} ...
```

Legacy validation remains valid:

```bash
pyepubcheck book.epub
```

That is treated as:

```bash
pyepubcheck check book.epub
```

## Validation command

`pyepubcheck check PATH`
: Validate a publication, package document, or content document.

`--mode`, `-m`
: Select one validation mode: `auto`, `opf`, `xhtml`, `svg`, `nav`, `mo`, or `exp`.

`-v EPUB_VERSION`
: Select the EPUB version string used in the validation report. The default is `3.0`.

`--profile`, `-p`
: Select a validation profile. Supported values are `default`, `dict`, `edupub`, `idx`, `preview`, and `accessibility`.

## Report output

`--out`, `-o`, `-out`
: Write XML report output to a file or to `-` for stdout.

`--json`, `-j`
: Write JSON report output to a file or to `-` for stdout.

`--xmp`, `-x`
: Write XMP report output to a file or to `-` for stdout.

Only one structured output option can be used at a time.

## Console filtering

`--quiet`, `-q`
: Suppress console output.

`--fatal`, `-f`
: Show only fatal messages.

`--error`, `-e`
: Show errors and fatal messages.

`--warn`, `-w`
: Show warnings, errors, and fatal messages.

`--usage`, `-u`
: Include usage messages in addition to warnings, errors, and fatal messages.

## Failure behavior

`--failonwarnings`
: Return exit code `1` when visible warnings are present.

## Localization and messages

`--locale LOCALE`
: Select a report locale where translations exist.

`--customMessages`, `-c`
: Load a custom message override file.

`--summary`
: Show a compact publication summary after a clean validation run. This is the default.

`--no-summary`
: Disable the clean-run publication summary.

## Archive helper

`--save`
: Save an expanded EPUB as an archive. This option requires `--mode exp` or no explicit mode.

## Inspection commands

`pyepubcheck inspect PATH`
: Inspect the publication and render text, JSON, or Markdown output.

```bash
pyepubcheck inspect book.epub
pyepubcheck inspect book.epub --format json
pyepubcheck inspect book.epub --estimate-pages --words-per-page 250
```

`pyepubcheck images PATH`
: Inspect manifested image assets.

```bash
pyepubcheck images book.epub --sort size --largest 10
pyepubcheck images book.epub --format csv
```

`pyepubcheck metadata PATH`
: Report stored OPF metadata without running validation.

`pyepubcheck manifest PATH`
: Report manifest items and file presence.

`pyepubcheck nav PATH`
: Report TOC, landmarks, and page-list information.

`pyepubcheck stats PATH`
: Report word and character estimates and optional estimated pages.

## Inspection output notes

- `inspect` supports `--include images,metadata,manifest,nav,stats,container`.
- `inspect`, `metadata`, `manifest`, `nav`, and `stats` support `--format`.
- `images` and `manifest` support CSV output.
- Inspection commands are read-only. They do not extract packaged EPUBs to disk or rewrite inputs.
- Estimated pages are only produced when `--estimate-pages` is supplied.
