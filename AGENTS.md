# AGENTS.md

This file provides guidance to AI agents when working with code in this repository.

## Project Overview

`certbot-dns-arsys` is a Certbot DNS authenticator plugin for Arsys domains. It fulfils DNS-01 ACME challenges by creating and deleting `_acme-challenge` TXT records via the Arsys Hosting SOAP API (endpoint: `api.servidoresdns.net:54321`). Distributed as a PyPI package and a Snap.

## Commands

```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest tests/

# Run a single test file
pytest tests/test_arsys_client.py

# Run a single test
pytest tests/test_arsys_client.py::TestCreateTxtRecord::test_success

# Run tests with coverage (must stay ≥ 85%)
pytest tests/ --cov=certbot_dns_arsys --cov-report=term-missing --cov-fail-under=85

# Lint
ruff check .

# Format
ruff format .

# Type-check
mypy certbot_dns_arsys/
```

## Architecture

```
certbot_dns_arsys/
  __init__.py                      # empty; marks the package
  _internal/
    dns_arsys.py                   # Authenticator (certbot.plugins.dns_common.DNSAuthenticator)
    arsys_client.py                # _ArsysClient — raw SOAP HTTP calls
```

**Data flow:**

1. Certbot calls `Authenticator._perform()` → `_ArsysClient.create_txt_record()` → SOAP `CreateDNSEntry`
2. `_wait_for_propagation()` polls authoritative nameservers (via dnspython) until the TXT record is visible, then returns
3. Certbot calls `Authenticator._cleanup()` → `_ArsysClient.delete_txt_record()` → SOAP `DeleteDNSEntry`

**`_ArsysClient`** (`arsys_client.py`):
- No third-party HTTP library — uses `urllib.request` and `xml.etree.ElementTree` only.
- Credentials (`api_login:api_key`) are sent as HTTP Basic Auth (Base64).
- SOAP envelope is encoded in ISO-8859-1 (Arsys API requirement).
- Delete is idempotent: error codes `{404, 1002, 1004}` from the API are silently ignored.

**`_wait_for_propagation`** (`dns_arsys.py`):
- Resolves the zone's authoritative NS, filters out private IPs, and queries those directly.
- Falls back to the system resolver if NS lookup fails or all NS IPs are private.
- Falls back to a plain `time.sleep` if `dnspython` is not installed.
- Polls every 15 s (`_POLL_INTERVAL`); logs a warning and proceeds on timeout rather than raising.

## Plugin Registration

The Certbot plugin entry point is declared in `pyproject.toml`:

```toml
[project.entry-points."certbot.plugins"]
dns-arsys = "certbot_dns_arsys._internal.dns_arsys:Authenticator"
```

## Credentials File

The plugin reads an INI file with keys: `dns_arsys_api_url` (optional), `dns_arsys_api_login`, `dns_arsys_api_key`, `dns_arsys_domain`. See `.secrets/.example_arsys.ini` for the template.

## Snap

`snap/snapcraft.yaml` builds the plugin as a `strict`-confinement snap on `core22`. It exposes a `certbot` content slot so the certbot snap can discover the plugin's Python packages, and uses a `certbot-metadata` plug that auto-connects to the certbot snap.

## Tooling

- **Linter / formatter**: ruff (`line-length = 100`, rules `E F W I UP`)
- **Type checker**: mypy (`strict = true`, `ignore_missing_imports = true`)
- **Test runner**: pytest with `--tb=short`; coverage threshold 85 %
- **CI**: GitHub Actions (`.github/workflows/test.yml`) — runs the full matrix (Python 3.10–3.13) on every push/PR

## Release process

Publishing to PyPI and the Snap Store is fully automated via CI and triggered by pushing a version tag:

1. Bump `version` in `pyproject.toml` (e.g. `"0.1.1"` → `"0.1.2"`).
2. Commit: `git commit -m "chore: bump version to X.Y.Z"`.
3. Tag: `git tag vX.Y.Z`.
4. Push both: `git push && git push --tags`.
5. CI runs `publish.yml` and `snap-publish.yml` automatically; both gate on the test suite.
6. Create a GitHub release for the new tag.

**Critical**: the version string in `pyproject.toml` is the version that ends up on PyPI and the Snap Store — the tag name is only a trigger. If you tag without bumping `pyproject.toml` first, CI will silently publish under the old version number (or fail as a duplicate if that version already exists).
