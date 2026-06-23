## MODIFIED Requirements

### Requirement: CI runs lint and tests on every push and PR
A GitHub Actions workflow `test.yml` SHALL trigger on `push` and `pull_request` to any branch. It SHALL run:
1. `ruff check .` (linting)
2. `mypy certbot_dns_arsys/` (type checking)
3. `pytest tests/` with coverage, producing both a terminal report and machine-readable reports: a JUnit XML test report (`--junitxml`) and a Cobertura coverage XML report (`--cov-report=xml`)

The workflow SHALL additionally:
- Write the coverage total to the GitHub Actions job summary (`$GITHUB_STEP_SUMMARY`)
- Upload the JUnit and coverage XML reports as a build artifact, named per Python version so matrix jobs do not collide

The job SHALL fail if any of the lint, type-check, or test steps exit with a non-zero code.

#### Scenario: Tests pass on PR
- **WHEN** a pull request is opened with passing code
- **THEN** the `test.yml` workflow SHALL complete with all steps green

#### Scenario: Tests fail on linting error
- **WHEN** code contains a `ruff` violation
- **THEN** the `test.yml` workflow SHALL fail and report the violation

#### Scenario: Test run publishes reports and coverage summary
- **WHEN** the `test.yml` workflow runs to completion
- **THEN** it SHALL upload JUnit and coverage XML artifacts named per Python version AND write the coverage total to the job summary
