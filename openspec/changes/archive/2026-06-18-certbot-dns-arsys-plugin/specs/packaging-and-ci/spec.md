## ADDED Requirements

### Requirement: Package uses pyproject.toml with correct metadata and entry points
The package SHALL be defined entirely in `pyproject.toml` using `setuptools>=61` as the build backend. It SHALL include:
- `name = "certbot-dns-arsys"`
- `version` managed manually (semver, starting at `0.1.0`)
- `requires-python = ">=3.11"`
- `dependencies`: `certbot>=2.0.0`, `acme>=2.0.0`, `dnspython>=2.0.0`
- `[project.entry-points."certbot.plugins"]`: `dns-arsys = certbot_dns_arsys._internal.dns_arsys:Authenticator`
- PyPI classifiers: Development Status Alpha, Intended Audience System Administrators, Topic Internet Security, License Apache 2.0, Python 3.11+

#### Scenario: Package installs correctly
- **WHEN** `pip install certbot-dns-arsys` is run in a Python 3.11+ environment with certbot present
- **THEN** `certbot plugins` SHALL list `dns-arsys` without errors

#### Scenario: Entry point registration
- **WHEN** the package is installed
- **THEN** `importlib.metadata.entry_points(group="certbot.plugins")` SHALL return an entry named `dns-arsys` pointing to `certbot_dns_arsys._internal.dns_arsys:Authenticator`

---

### Requirement: Package structure follows certbot plugin conventions
The source layout SHALL be:
```
certbot_dns_arsys/
├── __init__.py
└── _internal/
    ├── __init__.py
    ├── dns_arsys.py      # Authenticator class
    └── arsys_client.py   # _ArsysClient SOAP client
tests/
├── __init__.py
├── test_dns_arsys.py
└── test_arsys_client.py
Dockerfile
pyproject.toml
README.rst
LICENSE
.github/workflows/
├── test.yml
├── publish.yml
└── docker.yml
```

#### Scenario: Import path is clean
- **WHEN** `from certbot_dns_arsys._internal.dns_arsys import Authenticator` is executed
- **THEN** it SHALL succeed without errors

---

### Requirement: CI runs lint and tests on every push and PR
A GitHub Actions workflow `test.yml` SHALL trigger on `push` and `pull_request` to any branch. It SHALL run:
1. `ruff check .` (linting)
2. `mypy certbot_dns_arsys/` (type checking)
3. `pytest tests/ --cov=certbot_dns_arsys --cov-report=term-missing` (unit tests with coverage)

The job SHALL fail if any of these steps exit with a non-zero code.

#### Scenario: Tests pass on PR
- **WHEN** a pull request is opened with passing code
- **THEN** the `test.yml` workflow SHALL complete with all steps green

#### Scenario: Tests fail on linting error
- **WHEN** code contains a `ruff` violation
- **THEN** the `test.yml` workflow SHALL fail and report the violation

---

### Requirement: PyPI publishing is automated on version tags via OIDC
A GitHub Actions workflow `publish.yml` SHALL trigger on push of tags matching `v*.*.*`. It SHALL:
1. Build the distribution with `python -m build`
2. Publish to PyPI using `pypa/gh-action-pypi-publish` with Trusted Publisher (OIDC, no API token secret)

#### Scenario: New version tag triggers PyPI release
- **WHEN** a tag `v0.2.0` is pushed to the repository
- **THEN** the `publish.yml` workflow SHALL build and upload `certbot_dns_arsys-0.2.0-py3-none-any.whl` and `certbot_dns_arsys-0.2.0.tar.gz` to PyPI

---

### Requirement: Docker image is built and pushed on release
A GitHub Actions workflow `docker.yml` SHALL trigger on GitHub release publication. It SHALL:
1. Build a Docker image from the project `Dockerfile` (extending `certbot/certbot:latest`)
2. Tag the image as `ghcr.io/<owner>/certbot-dns-arsys:<version>` and `ghcr.io/<owner>/certbot-dns-arsys:latest`
3. Push to GitHub Container Registry (GHCR)

#### Scenario: Release triggers Docker build
- **WHEN** a GitHub release is published
- **THEN** the `docker.yml` workflow SHALL build and push the Docker image with the release version tag

---

### Requirement: Dockerfile extends certbot/certbot:latest
The `Dockerfile` SHALL use `FROM certbot/certbot:latest` as its base image and install the plugin via `pip install certbot-dns-arsys` (or `pip install .` for local builds). It SHALL not run as root in the CMD instruction.

#### Scenario: Docker image includes plugin
- **WHEN** the Docker image is built and `certbot plugins` is run inside it
- **THEN** `dns-arsys` SHALL appear in the output

---

### Requirement: Test suite covers all public behaviors with mocked API calls
Unit tests SHALL cover: SOAP envelope construction, Base64 auth encoding, `create_txt_record` success and error paths, `delete_txt_record` idempotency, propagation poller NS resolution fallback, poller timeout behavior, and authenticator credential loading. Tests SHALL NOT make real network calls — all HTTP and DNS calls SHALL be mocked.

#### Scenario: Test suite runs in isolation
- **WHEN** `pytest tests/` is run in a clean environment without network access
- **THEN** all tests SHALL pass

#### Scenario: Coverage threshold
- **WHEN** `pytest --cov=certbot_dns_arsys` is run
- **THEN** line coverage SHALL be ≥ 85%

---

### Requirement: README.rst documents installation and usage
`README.rst` SHALL include:
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
