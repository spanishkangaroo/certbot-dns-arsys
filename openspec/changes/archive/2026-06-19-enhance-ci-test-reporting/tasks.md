## 1. Emit machine-readable reports

- [x] 1.1 Update the pytest step in `test.yml` to add `--cov-report=xml` and `--junitxml=junit.xml` (keeping `term-missing` and `--cov-fail-under=85`)

## 2. Publish coverage summary and artifacts

- [x] 2.1 Add a step that parses `coverage.xml` and appends the coverage total to `$GITHUB_STEP_SUMMARY`
- [x] 2.2 Add an `actions/upload-artifact@v4` step (with `if: always()`) uploading `coverage.xml` and `junit.xml`, named `test-reports-${{ matrix.python-version }}`

## 3. Validate

- [x] 3.1 Confirm `test.yml` is valid YAML
- [x] 3.2 Verify locally that `pytest tests/ --cov=certbot_dns_arsys --cov-report=xml --junitxml=junit.xml` produces both files and the coverage parse works
- [x] 3.3 Run `openspec validate enhance-ci-test-reporting --strict` and resolve any issues
