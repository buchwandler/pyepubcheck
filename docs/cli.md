# Command-line interface

The console command is `pyepubcheck`.

```text
usage: pyepubcheck [-h] [--version] [--mode {opf,xhtml,svg,nav,mo,exp}]
                   [-v EPUB_VERSION]
                   [--profile {default,dict,edupub,idx,preview,accessibility}]
                   [--save] [--out XML_REPORT] [--json JSON_REPORT]
                   [--xmp XMP_REPORT] [--quiet] [--fatal] [--error] [--warn]
                   [--usage] [--failonwarnings] [--locale LOCALE]
                   [--customMessages CUSTOM_MESSAGES]
                   [path]
```

## Positional argument

`path`
: Publication, package document, or content document to validate.

## Validation selection

`--mode`, `-m`
: Select one validation mode: `opf`, `xhtml`, `svg`, `nav`, `mo`, or `exp`. Omit this option to let the validator choose automatically.

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

## Archive helper

`--save`
: Save an expanded EPUB as an archive. This option requires `--mode exp` or no explicit mode.
