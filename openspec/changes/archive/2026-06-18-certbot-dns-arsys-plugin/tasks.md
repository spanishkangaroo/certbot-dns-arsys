## 1. Project Scaffolding

- [x] 1.1 Create package directory structure: `certbot_dns_arsys/__init__.py`, `certbot_dns_arsys/_internal/__init__.py`, `certbot_dns_arsys/_internal/dns_arsys.py`, `certbot_dns_arsys/_internal/arsys_client.py`
- [x] 1.2 Create `tests/__init__.py`, `tests/test_dns_arsys.py`, `tests/test_arsys_client.py`
- [x] 1.3 Write `pyproject.toml` with name `certbot-dns-arsys`, `requires-python=">=3.11"`, dependencies (`certbot>=2.0.0`, `acme>=2.0.0`, `dnspython>=2.0.0`), entry point `dns-arsys = certbot_dns_arsys._internal.dns_arsys:Authenticator`, and PyPI classifiers
- [x] 1.4 Add `[project.optional-dependencies] dev = ["pytest", "pytest-cov", "ruff", "mypy"]` to `pyproject.toml`
- [x] 1.5 Create `LICENSE` file (Apache 2.0)
- [x] 1.6 Create `README.rst` with plugin description, prerequisites, installation, credentials format, example certbot command, Docker usage, and license section

## 2. SOAP Client (`arsys_client.py`)

- [x] 2.1 Implement `_ArsysClient.__init__(api_url, api_login, api_key, domain)` — store params, compute Base64 Basic Auth header, validate non-empty credentials
- [x] 2.2 Implement private `_ArsysClient._build_envelope(operation, **params)` — build SOAP 1.1 XML envelope string with ISO-8859-1 encoding and XML-escape all parameter values
- [x] 2.3 Implement private `_ArsysClient._call(operation, **params)` — send POST via `urllib.request` with `Content-Type: text/xml; charset=ISO-8859-1`, `SOAPAction`, and `Authorization` headers; 30s timeout; raise `PluginError` on HTTP error or `URLError`
- [x] 2.4 Implement private `_ArsysClient._parse_response(xml_bytes, operation)` — parse response with `xml.etree.ElementTree`, extract `errorCode` and `errorMsg`, raise `PluginError` if code != 0, raise `PluginError` on XML parse failure
- [x] 2.5 Implement `_ArsysClient.create_txt_record(name, value)` — call `CreateDNSEntry` with `dns=name`, `domain=self.domain`, `type="TXT"`, `value=value`
- [x] 2.6 Implement `_ArsysClient.delete_txt_record(name, value)` — call `DeleteDNSEntry` with same params; catch "not found" error codes and return without raising (idempotent)

## 3. Propagation Poller (`dns_arsys.py` or `_propagation.py`)

- [x] 3.1 Implement `_wait_for_propagation(record_name, value, timeout)` — try to import `dns.resolver`; if `ImportError`, sleep `timeout` seconds and log warning
- [x] 3.2 Implement `_authoritative_resolver(record_name)` — resolve zone NS records, resolve each NS hostname to A record, filter RFC-1918 IPs; if public IPs found, return resolver with those nameservers; otherwise fall back to system resolver with log message
- [x] 3.3 Implement polling loop in `_wait_for_propagation` — every 15s query TXT records for `record_name`; return immediately if `value` found; log elapsed time and TXT values (or exception) on each iteration; log warning and return (without raising) on timeout

## 4. DNS Authenticator (`dns_arsys.py`)

- [x] 4.1 Implement `Authenticator` class extending `certbot.plugins.dns_common.DNSAuthenticator` — set `description`, `ttl = 60`
- [x] 4.2 Implement `Authenticator.add_parser_arguments(cls, add)` — register `--dns-arsys-credentials` and `--dns-arsys-propagation-seconds` (default 120)
- [x] 4.3 Implement `Authenticator._setup_credentials()` — use `self._configure_credentials()` to load INI file; validate required keys `dns_arsys_api_login`, `dns_arsys_api_key`, `dns_arsys_domain`; apply default for `dns_arsys_api_url`
- [x] 4.4 Implement `Authenticator._perform(domain, validation_name, validation)` — instantiate `_ArsysClient` from loaded credentials; call `create_txt_record(f"_acme-challenge.{domain}", validation)`; call `_wait_for_propagation` with configured timeout
- [x] 4.5 Implement `Authenticator._cleanup(domain, validation_name, validation)` — call `delete_txt_record(f"_acme-challenge.{domain}", validation)`; catch and log any `PluginError` without re-raising

## 5. Unit Tests

- [x] 5.1 Write `tests/test_arsys_client.py`: test SOAP envelope construction (structure, XML escaping), Base64 auth header encoding, `create_txt_record` success path (mock `urllib.request.urlopen`), `create_txt_record` with non-zero errorCode raises `PluginError`, `create_txt_record` with timeout raises `PluginError`, `delete_txt_record` success path, `delete_txt_record` idempotent on not-found error, malformed XML response raises `PluginError`
- [x] 5.2 Write `tests/test_dns_arsys.py`: test authenticator credential loading from INI (valid and missing keys), `_perform` calls `create_txt_record` with correct name/value for standard domain, wildcard domain, and subdomain, `_cleanup` calls `delete_txt_record` correctly, `_cleanup` suppresses `PluginError` without re-raising, propagation timeout passed through correctly
- [x] 5.3 Write propagation poller tests: NS resolution returns public IPs → custom resolver used, all NS IPs private → system resolver used, NS resolution fails → system resolver used, TXT record found before timeout → returns immediately, TXT record not found within timeout → logs warning and returns, multiple TXT values → matches correctly, `ImportError` on dnspython → sleeps `timeout` seconds
- [x] 5.4 Verify `pytest --cov=certbot_dns_arsys` achieves ≥ 85% line coverage

## 6. Docker

- [x] 6.1 Write `Dockerfile` extending `FROM certbot/certbot:latest`; `COPY . /src` and `RUN pip install /src` (or `pip install certbot-dns-arsys` for registry-based builds); verify `certbot plugins` lists `dns-arsys`
- [x] 6.2 Test Docker image locally: `docker build -t certbot-dns-arsys .` and `docker run --rm certbot-dns-arsys plugins` should output `dns-arsys`

## 7. GitHub Actions CI/CD

- [x] 7.1 Write `.github/workflows/test.yml` — trigger on `push` and `pull_request`; matrix Python 3.11; steps: checkout, install dev deps, `ruff check .`, `mypy certbot_dns_arsys/`, `pytest tests/ --cov=certbot_dns_arsys --cov-report=term-missing`
- [x] 7.2 Write `.github/workflows/publish.yml` — trigger on `push` with `tags: ['v*.*.*']`; steps: checkout, build (`python -m build`), publish with `pypa/gh-action-pypi-publish` using Trusted Publisher (OIDC); configure PyPI Trusted Publisher in PyPI project settings
- [x] 7.3 Write `.github/workflows/docker.yml` — trigger on `release: published`; steps: checkout, log in to GHCR, `docker/build-push-action` to build and push `ghcr.io/<owner>/certbot-dns-arsys:<tag>` and `:latest`

## 8. Validation & Polish

- [x] 8.1 Read `docs/Manual de Usuario API Hosting.pdf` to confirm `CreateDNSEntry` and `DeleteDNSEntry` SOAP operation names, parameter names, and all `errorCode` values; update `arsys_client.py` idempotency handling if needed
- [x] 8.2 Run `pip install -e ".[dev]"` locally and verify `certbot plugins` lists `dns-arsys`
- [x] 8.3 Run a dry-run end-to-end test: `certbot certonly --dry-run --authenticator dns-arsys --dns-arsys-credentials /path/to/test.ini -d "*.yourdomain.com"`
- [x] 8.4 Run `ruff check .` and `mypy certbot_dns_arsys/` with zero errors
- [x] 8.5 Verify `README.rst` renders correctly with `python -m docutils README.rst /dev/null` or `rstcheck README.rst`
- [ ] 8.6 Tag `v0.1.0` and confirm the `publish.yml` and `docker.yml` workflows complete successfully
