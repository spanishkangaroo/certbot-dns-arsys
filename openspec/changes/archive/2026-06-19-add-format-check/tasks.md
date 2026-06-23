## 1. Format the codebase

- [x] 1.1 Run `ruff format .` to format the four unformatted files
- [x] 1.2 Confirm `ruff format --check .` now reports no changes needed
- [x] 1.3 Confirm `pytest tests/` still passes (formatting did not change behavior)

## 2. Add the formatting gate to CI

- [x] 2.1 Add a `ruff format --check .` step to `test.yml` immediately after the `ruff check .` step

## 3. Validate

- [x] 3.1 Confirm `test.yml` is valid YAML
- [x] 3.2 Run `openspec validate add-format-check --strict` and resolve any issues
