## Why

Arsys-hosted domains have no supported Certbot DNS plugin, forcing users to either perform manual DNS-01 challenges (breaking auto-renewal) or maintain fragile ad-hoc scripts. A proper third-party certbot plugin removes that friction and enables fully automated wildcard certificate issuance and renewal for any Arsys-managed domain.

## What Changes

- Introduce a new Python package `certbot-dns-arsys` that integrates with Certbot's authenticator plugin system
- Implement an `ArsysClient` wrapping the Arsys SOAP DNS API (`CreateDNSEntry` / `DeleteDNSEntry`) with HTTP Basic Auth
- Implement a `DNSAuthenticator` subclass that creates and removes `_acme-challenge` TXT records during the DNS-01 challenge lifecycle
- Add smart DNS propagation polling (authoritative NS via dnspython) with graceful fallback when Arsys NS IPs are private/unreachable
- Provide INI-format credentials file support following certbot plugin conventions
- Package with `pyproject.toml`, proper entry points, and classifiers for PyPI release
- Add a `Dockerfile` extending `certbot/certbot:latest` with the plugin pre-installed
- Add GitHub Actions workflows: lint+test on PR/push, auto-publish to PyPI on version tags, Docker image build on release

## Capabilities

### New Capabilities

- `arsys-soap-client`: SOAP client for the Arsys DNS API — handles Basic Auth, XML envelope construction, `CreateDNSEntry` and `DeleteDNSEntry` operations, and response error parsing
- `dns-authenticator`: Certbot `DNSAuthenticator` subclass that loads INI credentials, invokes the SOAP client to create/delete `_acme-challenge` TXT records, and waits for propagation
- `propagation-polling`: Smart DNS propagation checker — resolves authoritative nameservers for the zone, polls every 15s for TXT record visibility, falls back gracefully when NS IPs are private
- `packaging-and-ci`: PyPI packaging (`pyproject.toml`, entry points, classifiers) and GitHub Actions CI/CD (test, publish, Docker)

### Modified Capabilities

## Impact

- **New package**: `certbot-dns-arsys` (PyPI) / `certbot_dns_arsys` (Python import)
- **Dependencies added**: `certbot >=2.0.0`, `acme >=2.0.0`, `requests`, `dnspython`
- **Python**: 3.11+
- **No changes to existing code** — this is a greenfield package in a new repo
- **External API**: Arsys SOAP endpoint `https://api.servidoresdns.net:54321/hosting/api/soap/index.php`
- **Credentials**: INI file with `dns_arsys_api_url`, `dns_arsys_api_login`, `dns_arsys_api_key`, `dns_arsys_domain`
