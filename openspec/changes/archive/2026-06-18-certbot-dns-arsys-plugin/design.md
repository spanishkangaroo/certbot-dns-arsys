## Context

Certbot's official plugin ecosystem is closed to new DNS providers. Third-party plugins must be published independently and integrate via setuptools entry points under the `certbot.plugins` group. The Arsys DNS API uses an older SOAP/XML transport (not REST), encoded in ISO-8859-1, requiring a lightweight XML-building approach. Existing reference implementations (`certbot-dns-ispconfig`, `certbot-dns-duckdns`) provide established patterns for class hierarchy, credential loading, and propagation handling. The private `spt-certbot` repo already proves the SOAP operations and smart-polling logic work in production.

## Goals / Non-Goals

**Goals:**
- Implement a standards-compliant certbot DNS authenticator that can be discovered with `certbot plugins`
- Wrap the Arsys SOAP API with a clean client that has no external SOAP library dependency
- Support wildcard certificates (`*.example.com`) and multi-domain (`-d a.com -d b.com`) via a single plugin invocation
- Ship a smart DNS propagation poller that queries authoritative nameservers and handles Arsys's private-IP NS addresses
- Provide INI-format credentials file matching certbot conventions
- Publish to PyPI via automated GitHub Actions with OIDC Trusted Publishers
- Provide a Docker image extending `certbot/certbot:latest`

**Non-Goals:**
- Supporting the Arsys CloudBuilder REST API or Multi-Domain Management API — only the Hosting SOAP API
- YAML credentials format (INI only, following certbot conventions)
- Manual-hook mode or standalone renewal scripts (users wanting that have `spt-certbot`)
- Auto-discovery of Arsys zones via API guessing (explicit `dns_arsys_domain` in credentials)
- Python < 3.11

## Decisions

### D1: No SOAP library — hand-rolled XML templates

**Decision**: Build SOAP envelopes with string formatting, parse responses with `xml.etree.ElementTree`.

**Rationale**: `zeep` and `suds` are heavyweight with their own bugs and installation complexity. The Arsys SOAP API uses a small, fixed envelope shape (one operation, a handful of typed params). A template string + ElementTree is ~30 lines and has zero extra dependencies.

**Alternatives**: `zeep` — rejected (adds 5+ transitive deps, overkill for 3 operations); `requests-xml` — rejected (unmaintained).

---

### D2: `urllib.request` for the SOAP HTTP call

**Decision**: Use stdlib `urllib.request` rather than `requests` for the SOAP client.

**Rationale**: The SOAP call is a single POST with custom headers. Using stdlib avoids an extra dependency and matches the pattern in `certbot_renewal.py` (which already works in production). If the `DNSAuthenticator` layer needs `requests` for other things, it can bring it in; the client stays pure stdlib.

**Alternatives**: `requests` — kept as fallback if TLS edge cases appear; `httpx` — rejected (async not needed).

---

### D3: Explicit domain in credentials, no zone auto-discovery

**Decision**: Require `dns_arsys_domain` in the INI file. No API calls to guess the zone.

**Rationale**: Arsys's SOAP API has no zone-listing endpoint documented. Auto-discovery would require trying progressively shorter suffixes and catching errors — fragile and slow. An explicit domain is clearer, easier to debug, and matches how users think about their Arsys account (one domain per account).

**Alternatives**: Auto-discover via suffix guessing — rejected (undocumented, brittle); multi-domain account support — deferred (no known use case yet).

---

### D4: Smart propagation polling with authoritative NS fallback

**Decision**: After `CreateDNSEntry`, query the zone's authoritative nameservers using `dnspython`. If all NS IPs are RFC-1918/private (Arsys internal infrastructure), fall back to the system resolver. Poll every 15s up to `propagation_seconds` (default 120). If not confirmed within the timeout, log a warning and proceed (Let's Encrypt will retry if validation fails).

**Rationale**: Arsys nameservers (`dnsNN.servidoresdns.net`) resolve to private IPs in some network contexts (observed in the private `spt-certbot` repo). A hard failure on unreachable NS would break the plugin in those environments. The graceful fallback preserves the safety property: we try hard to verify, but we don't block certificate issuance for a network configuration we can't control.

**Alternatives**: Fixed sleep — rejected (wastes time when propagation is fast; offers no feedback); dnspython required without fallback — rejected (breaks in restricted networks).

---

### D5: Plugin class hierarchy following certbot-dns-ispconfig

**Decision**: `Authenticator` extends `certbot.plugins.dns_common.DNSAuthenticator`. The SOAP client is a separate `_ArsysClient` class. Entry point: `certbot.plugins = dns-arsys = certbot_dns_arsys._internal.dns_arsys:Authenticator`.

**Rationale**: `DNSAuthenticator` handles all the plumbing (argument parsing, credential file loading, propagation seconds CLI arg). We only need to implement `_setup_credentials()`, `_perform()`, and `_cleanup()`. This is the proven pattern across all third-party certbot DNS plugins.

---

### D6: pyproject.toml (no setup.py)

**Decision**: Pure `pyproject.toml` with `[build-system] requires = ["setuptools>=61"]`.

**Rationale**: Modern Python packaging standard. `setup.py` is legacy and being deprecated by setuptools. All classifiers, entry points, and optional deps live in one file.

---

### D7: PyPI publishing via OIDC Trusted Publishers

**Decision**: GitHub Actions workflow with `pypa/gh-action-pypi-publish` using Trusted Publisher (no API token stored as secret).

**Rationale**: More secure than API tokens (no secret to rotate/leak). Supported natively by PyPI since 2023. Triggered on `v*` git tags.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Arsys SOAP API changes envelope format or adds auth requirements | Client is isolated in `_ArsysClient`; update one file. Version pin in requirements. |
| `CreateDNSEntry` succeeds but record doesn't propagate within 120s | Plugin logs a warning and proceeds; Let's Encrypt will retry. User can increase `--dns-arsys-propagation-seconds`. |
| Arsys SOAP API returns ISO-8859-1 characters in error messages | Decode response bytes as `iso-8859-1` before parsing; ElementTree handles it. |
| Port 54321 blocked by firewall | Document clearly in README. No workaround; users must whitelist the port. |
| `DeleteDNSEntry` fails after validation (cleanup error) | Log the error but do not fail the overall certbot run (certbot calls cleanup in a non-critical context). |
| dnspython not installed | `propagation-polling` gracefully degrades to fixed wait if dnspython import fails. |

## Migration Plan

Greenfield package — no migration needed. Users with existing `spt-certbot` manual-hook scripts can switch to the plugin by:
1. `pip install certbot-dns-arsys`
2. Create `~/.secrets/certbot/arsys.ini` from the existing YAML config
3. Replace manual `--manual-auth-hook` flags with `--authenticator dns-arsys --dns-arsys-credentials ~/.secrets/certbot/arsys.ini`

## Open Questions

- Does the Arsys SOAP API support creating multiple TXT records with the same name (needed when multiple `_acme-challenge` challenges run concurrently for SAN certs)? If not, plugin may need to serialize concurrent runs or use a lock file. **Assumption**: allow duplicates; to be validated during implementation.
- What error codes does Arsys return for "record already exists" vs "record not found"? Need to read `Manual de Usuario API Hosting.pdf` during implementation to confirm `errorCode` values and handle idempotency correctly.
