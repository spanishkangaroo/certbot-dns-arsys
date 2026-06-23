## MODIFIED Requirements

### Requirement: README.rst documents installation and usage
`README.rst` SHALL include:
- A row of status badges at the top of the file, immediately after the title: PyPI version, License (Apache 2.0), supported Python versions, and CI test status (the `test.yml` workflow). Each badge SHALL link to its corresponding page (PyPI project page, license file, and the Actions workflow).
- Plugin description and provider link
- Prerequisites (certbot, Python 3.11+)
- Installation instructions (`pip install certbot-dns-arsys`)
- Credentials file format and example
- Example `certbot certonly` command for a wildcard certificate
- Docker usage example
- A Troubleshooting section covering, at minimum: the plugin not being listed by `certbot plugins`, API authentication errors, connectivity to the non-standard API port (`api.servidoresdns.net:54321`), DNS propagation/validation timeouts (referencing `--dns-arsys-propagation-seconds`), and credentials-file permission errors
- Link to Arsys API documentation
- License section (Apache 2.0)

#### Scenario: README renders correctly on PyPI
- **WHEN** the package is published to PyPI
- **THEN** the project page SHALL display the RST-formatted README without rendering errors

#### Scenario: Badges display at the top of the README
- **WHEN** the README is viewed on GitHub or PyPI
- **THEN** a row of badges (PyPI version, license, Python versions, CI status) SHALL appear at the top, each linking to its corresponding page

#### Scenario: Troubleshooting section is present
- **WHEN** a user reads the README
- **THEN** a Troubleshooting section SHALL document the common failure modes (plugin not found, authentication errors, API port connectivity, propagation timeouts, credentials permissions) with guidance for each
