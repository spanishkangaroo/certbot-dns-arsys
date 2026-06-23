## ADDED Requirements

### Requirement: Plugin is discoverable by certbot
The `Authenticator` class SHALL be registered as a certbot plugin via a setuptools entry point in `pyproject.toml` under `[project.entry-points."certbot.plugins"]` as `dns-arsys = certbot_dns_arsys._internal.dns_arsys:Authenticator`. Running `certbot plugins` SHALL list `dns-arsys`.

#### Scenario: Plugin appears in certbot plugin list
- **WHEN** the package is installed and `certbot plugins` is run
- **THEN** `dns-arsys` SHALL appear in the output

---

### Requirement: Authenticator loads credentials from INI file
The plugin SHALL accept a credentials file path via the `--dns-arsys-credentials` CLI argument. The INI file SHALL define the following keys under the `certbot_dns_arsys` prefix:
- `dns_arsys_api_url` (optional, defaults to `https://api.servidoresdns.net:54321/hosting/api/soap/index.php`)
- `dns_arsys_api_login` (required)
- `dns_arsys_api_key` (required)
- `dns_arsys_domain` (required)

#### Scenario: All required keys present
- **WHEN** an INI file with `dns_arsys_api_login`, `dns_arsys_api_key`, and `dns_arsys_domain` is provided
- **THEN** the authenticator SHALL initialize successfully

#### Scenario: Missing required key
- **WHEN** an INI file is missing `dns_arsys_api_login` or `dns_arsys_api_key` or `dns_arsys_domain`
- **THEN** certbot SHALL raise an error before attempting any DNS operation

#### Scenario: Default API URL is used when not specified
- **WHEN** `dns_arsys_api_url` is absent from the credentials file
- **THEN** the client SHALL use `https://api.servidoresdns.net:54321/hosting/api/soap/index.php`

---

### Requirement: Authenticator creates _acme-challenge TXT record on perform
When certbot calls `_perform(domain, validation_name, validation)`, the authenticator SHALL call `_ArsysClient.create_txt_record()` with `name=f"_acme-challenge.{domain}"` and `value=validation`. After creation, it SHALL invoke the propagation poller before returning.

#### Scenario: Perform creates TXT record for a standard domain
- **WHEN** `_perform("example.com", "_acme-challenge.example.com", "token123")` is called
- **THEN** `_ArsysClient.create_txt_record("_acme-challenge.example.com", "token123")` SHALL be called exactly once

#### Scenario: Perform creates TXT record for a wildcard domain
- **WHEN** certbot requests validation for `*.example.com`
- **THEN** `_ArsysClient.create_txt_record("_acme-challenge.example.com", "<token>")` SHALL be called

#### Scenario: Perform creates TXT record for a subdomain
- **WHEN** certbot requests validation for `sub.example.com`
- **THEN** `_ArsysClient.create_txt_record("_acme-challenge.sub.example.com", "<token>")` SHALL be called

---

### Requirement: Authenticator deletes _acme-challenge TXT record on cleanup
When certbot calls `_cleanup(domain, validation_name, validation)`, the authenticator SHALL call `_ArsysClient.delete_txt_record()` with the same `name` and `value` used during perform. Cleanup errors SHALL be logged but SHALL NOT raise, so they do not block certificate issuance.

#### Scenario: Cleanup removes TXT record
- **WHEN** `_cleanup("example.com", "_acme-challenge.example.com", "token123")` is called
- **THEN** `_ArsysClient.delete_txt_record("_acme-challenge.example.com", "token123")` SHALL be called exactly once

#### Scenario: Cleanup error does not abort certbot run
- **WHEN** `delete_txt_record` raises `PluginError` during cleanup
- **THEN** the authenticator SHALL log the error and return normally without re-raising

---

### Requirement: Propagation seconds configurable via CLI
The authenticator SHALL expose `--dns-arsys-propagation-seconds` as a CLI argument (default: `120`). This value SHALL be passed to the propagation poller as the maximum wait time.

#### Scenario: Custom propagation seconds accepted
- **WHEN** `--dns-arsys-propagation-seconds 300` is passed on the CLI
- **THEN** the propagation poller SHALL use 300 as the timeout

#### Scenario: Default propagation seconds used when not specified
- **WHEN** `--dns-arsys-propagation-seconds` is not passed
- **THEN** the propagation poller SHALL use 120 seconds as the timeout
