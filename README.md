# pyepubcheck

Clean-room Python reimplementation of EPUBCheck behavior, driven by the imported
EPUBCheck Gherkin corpus under `specs/behavior/features`.

## Development

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
python -m pyepubcheck --version
specmason corpus inspect --config specmason.toml --json
```

The package layout intentionally lives at `./pyepubcheck` and not `src/`.
