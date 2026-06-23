## 1. Add Dependabot configuration

- [x] 1.1 Create `.github/dependabot.yml` with `version: 2` and `updates` entries for the `pip` and `github-actions` ecosystems, both on a weekly schedule
- [x] 1.2 Verify the file is valid YAML and contains both ecosystems

## 2. Validate

- [x] 2.1 Run `openspec validate add-dependabot --strict` and resolve any issues
- [x] 2.2 Confirm existing test suite still passes (`pytest tests/`)
