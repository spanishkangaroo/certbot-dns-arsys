## Why

The project has no GitHub funding metadata, so the repository does not surface a "Sponsor" button or signal that the maintainer is open to support. Adding a `.github/FUNDING.yml` is a low-effort, common convention across the certbot DNS plugin ecosystem (Feature #10 in `docs/dns-plugins-research.md`) that improves project credibility and discoverability.

## What Changes

- Add a `.github/FUNDING.yml` file declaring the project's sponsorship channel(s), enabling GitHub's "Sponsor" button on the repository.
- Use the GitHub Sponsors `github:` entry for the owner `spanishkangaroo`.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `packaging-and-ci`: Add a requirement that the repository ships a valid GitHub `FUNDING.yml` so sponsorship channels are surfaced on GitHub.

## Impact

- New file: `.github/FUNDING.yml`.
- No runtime, packaging, or API impact; affects GitHub repository community metadata only.
- No changes to Python code, dependencies, or CI workflows.
