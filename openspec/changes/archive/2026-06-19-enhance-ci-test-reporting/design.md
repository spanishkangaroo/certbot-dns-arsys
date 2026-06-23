## Context

`test.yml` runs a matrix over Python 3.11/3.12/3.13. Each job runs ruff, mypy, then `pytest tests/ --cov=certbot_dns_arsys --cov-report=term-missing --cov-fail-under=85`. `pytest-cov` and `coverage` are already dev dependencies.

## Decisions

- **Report formats**: add `--cov-report=xml` (Cobertura) and `--junitxml=junit.xml` to the existing pytest invocation; keep `term-missing` and `--cov-fail-under=85`.
- **Coverage summary**: after pytest, run `python -m coverage report` parsing, or simpler, use `coverage json`/`xml` already produced — append a one-line total using `python -c` reading `coverage.xml` line-rate to `$GITHUB_STEP_SUMMARY`.
- **Artifact naming**: `test-reports-${{ matrix.python-version }}` so the three matrix jobs upload distinct artifacts (`actions/upload-artifact@v4` requires unique names).
- **`if: always()`** on the upload step so reports are captured even when tests fail (the failure information is the most valuable case).

## Risks / Trade-offs

- Parsing `coverage.xml` for the summary keeps the step dependency-free (stdlib `xml`), avoiding extra tooling.
- Artifacts add minor storage; acceptable and they expire by default retention.
