## 1. Add Troubleshooting section

- [x] 1.1 Insert a `Troubleshooting` section in `README.rst` (after Options, before Notes) covering: plugin not listed by `certbot plugins`, API authentication errors, connectivity to `api.servidoresdns.net:54321`, propagation/validation timeouts (`--dns-arsys-propagation-seconds`), and credentials-file permission errors
- [x] 1.2 Add the section to the table-of-contents depth if needed (it uses `:local:` so no manual entry required)

## 2. Validate

- [x] 2.1 Verify the RST renders without errors (docutils parse)
- [x] 2.2 Run `openspec validate add-readme-troubleshooting --strict` and resolve any issues
- [x] 2.3 Confirm existing test suite still passes (`pytest tests/`)
