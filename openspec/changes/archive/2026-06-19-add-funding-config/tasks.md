## 1. Validation test (TDD — write first, expect failure)

- [x] 1.1 Add `pyyaml` to the `dev` optional-dependencies in `pyproject.toml` (used by the validation test)
- [x] 1.2 Add `tests/test_funding.py` that parses `.github/FUNDING.yml` and asserts: it is valid YAML mapping; it has a `github` key naming `spanishkangaroo`; every top-level key is a recognized GitHub funding platform. Run it and confirm it FAILS (file missing).

## 2. Implementation

- [x] 2.1 Create `.github/FUNDING.yml` with a `github: spanishkangaroo` entry
- [x] 2.2 Run `pytest tests/test_funding.py` and confirm it PASSES

## 3. Verify full gate

- [x] 3.1 Run `ruff check .`, `ruff format --check .`, `mypy certbot_dns_arsys/`, and full `pytest` with coverage; confirm all green
