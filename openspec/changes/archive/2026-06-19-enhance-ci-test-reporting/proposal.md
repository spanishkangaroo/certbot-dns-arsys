## Why

CI already runs the unit tests across Python 3.11–3.13 (feature #4 baseline), but the results are only visible by scrolling the raw job log. Mature setups surface test/coverage results as artifacts and in the run summary so failures and coverage trends are easy to inspect from the Actions UI without an external service.

## What Changes

- Emit machine-readable test and coverage reports from the `pytest` step: JUnit XML (`--junitxml`) and Cobertura coverage XML (`--cov-report=xml`).
- Write the coverage total to the GitHub Actions job summary (`$GITHUB_STEP_SUMMARY`).
- Upload the coverage and test-result XML as a build artifact, named per Python version to avoid collisions across the matrix.

## Capabilities

### New Capabilities

### Modified Capabilities

- `packaging-and-ci`: The CI test requirement is extended to require XML reports, a coverage job summary, and artifact upload.

## Impact

- Changes `.github/workflows/test.yml` only; no code or runtime impact on the plugin.
- No external services (Codecov etc.) are introduced; reporting stays inside GitHub.
