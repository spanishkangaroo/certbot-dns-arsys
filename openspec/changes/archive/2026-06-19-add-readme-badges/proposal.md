## Why

Leading certbot DNS plugins (lightsail, azure, godaddy, bunny, duckdns, porkbun, stackit, ionos, cdmon, hetzner-cloud) display status badges at the top of their README. Badges are an instant credibility signal, cost nothing at runtime, and are trivial to add. `certbot-dns-arsys` currently has none.

## What Changes

- Add a row of status badges to the top of `README.rst`:
  - PyPI version
  - License (Apache 2.0)
  - Supported Python versions
  - CI test status (the `test.yml` GitHub Actions workflow)
- Badges link to the corresponding project pages (PyPI, license file, Actions workflow).

## Capabilities

### New Capabilities

### Modified Capabilities

- `packaging-and-ci`: The README documentation requirement is extended to require a badge row at the top of `README.rst`.

## Impact

- Documentation-only change to `README.rst`; no code or runtime impact.
- Badges render on both GitHub and the PyPI project page.
