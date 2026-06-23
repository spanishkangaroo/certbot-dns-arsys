## Why

The cdmon and czechia plugins include detailed Troubleshooting sections covering the most common failure modes (permission errors, API authentication errors, DNS propagation issues). This is high user value and reduces support burden — it is just documentation. `certbot-dns-arsys` currently has only a brief "Notes" section.

## What Changes

- Add a `Troubleshooting` section to `README.rst` covering the failure modes specific to this plugin:
  - Plugin not found / not listed by `certbot plugins`
  - API authentication errors (bad `api_key` / `api_login`)
  - Connectivity to the non-standard port `api.servidoresdns.net:54321`
  - DNS propagation / validation timeouts (and the `--dns-arsys-propagation-seconds` flag)
  - File permission errors on the credentials file

## Capabilities

### New Capabilities

### Modified Capabilities

- `packaging-and-ci`: The README documentation requirement is extended to require a Troubleshooting section.

## Impact

- Documentation-only change to `README.rst`; no code or runtime impact.
