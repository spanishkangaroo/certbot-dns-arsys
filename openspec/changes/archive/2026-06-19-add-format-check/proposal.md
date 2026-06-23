## Why

CI already lints with `ruff check` and type-checks with `mypy` (feature #6 baseline), but it does not enforce a consistent code *format*. Plugins like duckdns and porkbun run a dedicated formatting check so style stays uniform and diffs stay clean. The codebase currently has four files that are not formatted to `ruff format`'s style.

## What Changes

- Format the existing source and tests with `ruff format` (style-only changes, no behavior change).
- Add a `ruff format --check .` step to the `test.yml` workflow so unformatted code fails CI.

## Capabilities

### New Capabilities

### Modified Capabilities

- `packaging-and-ci`: The CI requirement is extended to require a `ruff format --check` formatting gate alongside `ruff check` and `mypy`.

## Impact

- Reformats four files (`arsys_client.py`, `dns_arsys.py`, `test_dns_arsys.py`, `test_propagation.py`) — formatting only.
- Adds one CI step; future unformatted code is rejected on PRs.
