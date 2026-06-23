## Why

Several leading certbot DNS plugins (godaddy, duckdns, porkbun, ionos) enable Dependabot to keep dependencies fresh automatically. It is a small YAML file with high payoff: security and version updates are proposed as PRs without manual tracking. `certbot-dns-arsys` currently has no dependency automation.

## What Changes

- Add `.github/dependabot.yml` configuring weekly update checks for two ecosystems:
  - `pip` (Python dependencies declared in `pyproject.toml`)
  - `github-actions` (action versions pinned in `.github/workflows/`)

## Capabilities

### New Capabilities

### Modified Capabilities

- `packaging-and-ci`: A new requirement is added for automated dependency updates via Dependabot.

## Impact

- Adds one configuration file; no code or runtime impact.
- Dependabot will open PRs for outdated pip dependencies and GitHub Actions.
