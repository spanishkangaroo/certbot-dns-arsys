## ADDED Requirements

### Requirement: Dependency updates are automated via Dependabot
A `.github/dependabot.yml` file SHALL configure Dependabot to check for updates on a weekly schedule for two package ecosystems:
1. `pip` — Python dependencies (directory `/`, reading `pyproject.toml`)
2. `github-actions` — action versions used in `.github/workflows/` (directory `/`)

#### Scenario: Dependabot config is valid and covers both ecosystems
- **WHEN** `.github/dependabot.yml` is parsed
- **THEN** it SHALL declare `version: 2` and contain `updates` entries for both the `pip` and `github-actions` package ecosystems, each with a weekly schedule

#### Scenario: Outdated dependency triggers a PR
- **WHEN** a dependency in `pyproject.toml` or a GitHub Action has a newer version available
- **THEN** Dependabot SHALL open a pull request proposing the update
