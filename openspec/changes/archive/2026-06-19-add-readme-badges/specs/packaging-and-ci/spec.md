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
- Link to Arsys API documentation
- License section (Apache 2.0)

#### Scenario: README renders correctly on PyPI
- **WHEN** the package is published to PyPI
- **THEN** the project page SHALL display the RST-formatted README without rendering errors

#### Scenario: Badges display at the top of the README
- **WHEN** the README is viewed on GitHub or PyPI
- **THEN** a row of badges (PyPI version, license, Python versions, CI status) SHALL appear at the top, each linking to its corresponding page
