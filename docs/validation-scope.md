# Validation scope

This project is driven by the behavior corpus under `specs/behavior/features` and by Python tests mapped to those scenarios with SpecMason.

## Current validator areas

The package contains validators for these areas:

| Area                                | Package module                       |
| ----------------------------------- | ------------------------------------ |
| OCF/container/package discovery     | `pyepubcheck.checks.ocf`             |
| Package document rules              | `pyepubcheck.checks.package`         |
| EPUB 2 and NCX rules                | `pyepubcheck.checks.epub2`           |
| XHTML content documents             | `pyepubcheck.checks.xhtml`           |
| XHTML parsing and identifier checks | `pyepubcheck.xhtml_validator`        |
| SVG content                         | `pyepubcheck.checks.svg`             |
| CSS content                         | `pyepubcheck.checks.css`             |
| Navigation documents                | `pyepubcheck.checks.navigation`      |
| Fixed-layout and rendition metadata | `pyepubcheck.checks.layout`          |
| Media overlays                      | `pyepubcheck.checks.media_overlays`  |
| Referenced resources                | `pyepubcheck.checks.resources`       |
| Reporting and usage messages        | `pyepubcheck.checks.reporting_usage` |
| Profile-specific rules              | `pyepubcheck.checks.profiles.*`      |

## Supported profiles

| Profile         | Purpose                                                        |
| --------------- | -------------------------------------------------------------- |
| `default`       | Baseline validation behavior.                                  |
| `dict`          | EPUB dictionaries behavior.                                    |
| `edupub`        | EDUPUB profile behavior.                                       |
| `idx`           | EPUB indexes behavior.                                         |
| `preview`       | EPUB previews behavior.                                        |
| `accessibility` | Accessibility profile behavior currently covered by the tests. |

## Behavior corpus areas

The imported feature directories include CLI, CSS, EPUB 2, EPUB 3, localization, reporting, profile packages, multiple renditions, region navigation, and stress scenarios.

## Parity policy

`pyepubcheck` should document and test each EPUBCheck-compatible behavior before presenting it as supported. When adding validation behavior:

1. Add or import the Gherkin scenario.
2. Map the scenario in SpecMason.
3. Add an acceptance test.
4. Implement the validator.
5. Run both pytest and SpecMason checks.

## Known alpha limitation

This release is behavior-driven and incremental. It does not claim complete parity with every EPUBCheck validation rule, output message, localization string, or edge case.
