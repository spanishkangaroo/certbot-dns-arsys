## Context

`test.yml` runs `ruff check .` then `mypy`. `ruff` is already a dev dependency and `[tool.ruff]` is configured in `pyproject.toml` (`line-length = 100`, `target-version = "py311"`). `ruff format` uses the same config. Four files are currently unformatted.

## Decisions

- **Format first, then gate**: run `ruff format` once to bring the four files into compliance in the same change, so the new check passes immediately. Formatting changes are style-only and verified by the unchanged test suite.
- **Step placement**: add `ruff format --check .` directly after the existing `ruff check .` step, since both are ruff-based lint gates.
- **No config changes**: rely on the existing `[tool.ruff]` config; no new options needed.

## Risks / Trade-offs

- Reformatting touches four files in one commit; reviewers see a style-only diff. This is a one-time cost that keeps all future diffs clean.
