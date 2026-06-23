## Purpose

Defines how `certbot-dns-arsys` is packaged, documented, tested, and released: the `pyproject.toml` metadata and entry points, source layout, GitHub Actions CI (lint, type check, tests), automated PyPI and Docker publishing, and README documentation.
## Requirements
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
2. `ruff format --check .` (formatting check)
3. `mypy certbot_dns_arsys/` (type checking)
4. `pytest tests/` with coverage, producing both a terminal report and machine-readable reports: a JUnit XML test report (`--junitxml`) and a Cobertura coverage XML report (`--cov-report=xml`)

The workflow SHALL additionally:
- Write the coverage total to the GitHub Actions job summary (`$GITHUB_STEP_SUMMARY`)
- Upload the JUnit and coverage XML reports as a build artifact, named per Python version so matrix jobs do not collide

The job SHALL fail if any of the lint, format, type-check, or test steps exit with a non-zero code.

#### Scenario: Tests pass on PR
- **WHEN** a pull request is opened with passing code
- **THEN** the `test.yml` workflow SHALL complete with all steps green

#### Scenario: Tests fail on linting error
- **WHEN** code contains a `ruff` violation
- **THEN** the `test.yml` workflow SHALL fail and report the violation

#### Scenario: CI fails on unformatted code
- **WHEN** code is not formatted to `ruff format`'s style
- **THEN** the `ruff format --check .` step SHALL fail the workflow

#### Scenario: Test run publishes reports and coverage summary
- **WHEN** the `test.yml` workflow runs to completion
- **THEN** it SHALL upload JUnit and coverage XML artifacts named per Python version AND write the coverage total to the job summary

### Requirement: PyPI publishing is automated on version tags via OIDC
A GitHub Actions workflow `publish.yml` SHALL trigger on push of tags matching `v*.*.*`. It SHALL:
1. Run the unit test suite (`pytest`) in the build job before building; a failing test SHALL abort the release.
2. Build the distribution with `python -m build`
3. Generate signed build provenance attestations for the built distribution artifacts using `actions/attest-build-provenance` (requires `id-token: write` and `attestations: write` permissions on the build job)
4. Publish to PyPI using `pypa/gh-action-pypi-publish` with Trusted Publisher (OIDC, no API token secret)

#### Scenario: New version tag triggers PyPI release
- **WHEN** a tag `v0.2.0` is pushed to the repository
- **THEN** the `publish.yml` workflow SHALL build and upload `certbot_dns_arsys-0.2.0-py3-none-any.whl` and `certbot_dns_arsys-0.2.0.tar.gz` to PyPI

#### Scenario: Failing tests abort the release
- **WHEN** a tag is pushed but the test suite fails
- **THEN** the build job SHALL fail and no artifacts SHALL be published to PyPI

#### Scenario: Released artifacts carry build provenance
- **WHEN** the build job produces the distribution artifacts
- **THEN** it SHALL generate build provenance attestations for those artifacts before publishing

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

### Requirement: Dependency updates are automated via Dependabot
A `.github/dependabot.yml` file SHALL configure Dependabot to check for updates on a weekly schedule for two package ecosystems:
1. `pip` — Python dependencies (directory `/`, reading `pyproject.toml`)
2. `github-actions` — action versions used in `.github/workflows/` (directory `/`)

#### Scenario: Dependabot config is valid and covers both ecosystems
- **WHEN** `.github/dependabot.yml` is parsed
- **THEN** it SHALL declare `version: 2` and contain `updates` entries for both the `pip` and `github-actions` package ecosystems, each with a weekly schedule

#### Scenario: Outdated dependency triggers a PR
- **WHEN** a dependency in `pyproject.toml` or a GitHub Action has a newer version available
- **THEN** Dependabot SHALL open a pull request proposing the update

### Requirement: Docker image build is verified in CI
A GitHub Actions workflow `docker-build.yml` SHALL trigger on `push` and `pull_request` to any branch. It SHALL:
1. Build the Docker image from the project `Dockerfile` without pushing it to any registry.
2. Run `certbot plugins` inside the freshly built image and assert that `dns-arsys` appears in the output.

The job SHALL fail if the image fails to build or if `dns-arsys` is not registered.

#### Scenario: Dockerfile builds and registers the plugin
- **WHEN** a push or pull request triggers `docker-build.yml`
- **THEN** the image SHALL build successfully AND `certbot plugins` run inside it SHALL list `dns-arsys`

#### Scenario: Broken Dockerfile fails CI
- **WHEN** a change breaks the Docker build or prevents the plugin from registering
- **THEN** the `docker-build.yml` workflow SHALL fail

---

### Requirement: Repository declares sponsorship via FUNDING.yml
The repository SHALL include a `.github/FUNDING.yml` file so GitHub surfaces a "Sponsor" button for the project. The file SHALL be valid YAML using GitHub's funding schema and SHALL declare at least one funding channel. It SHALL include a `github:` entry naming the maintainer `spanishkangaroo`.

#### Scenario: FUNDING.yml exists and is valid YAML
- **WHEN** `.github/FUNDING.yml` is parsed as YAML
- **THEN** parsing SHALL succeed AND the result SHALL be a mapping

#### Scenario: GitHub sponsorship channel is declared
- **WHEN** `.github/FUNDING.yml` is parsed
- **THEN** it SHALL contain a `github` key whose value names `spanishkangaroo` (as a string or within a list)

#### Scenario: Only recognized funding platform keys are used
- **WHEN** `.github/FUNDING.yml` is parsed
- **THEN** every top-level key SHALL be one of GitHub's recognized funding platforms (e.g. `github`, `patreon`, `open_collective`, `ko_fi`, `tidelift`, `community_bridge`, `liberapay`, `issuehunt`, `lfx_membership`, `polar`, `buy_me_a_coffee`, `thanks_dev`, `custom`)

---

### Requirement: Plugin ships a Snap recipe for the certbot snap
The repository SHALL include a `snap/snapcraft.yaml` that builds `certbot-dns-arsys` as a strictly-confined snap installable into the certbot snap. The recipe SHALL:
- declare `name: certbot-dns-arsys`, `confinement: strict`, and `grade: stable`
- declare a `base` (a `core*` base such as `core20`/`core22`/`core24`)
- build the plugin via a `parts` entry using the `python` plugin sourced from the repository root
- expose the plugin to certbot through the content interface: a `slots` entry of `interface: content` advertising `content: certbot-1`, and a `plugs` entry `certbot-metadata` of `interface: content` advertising `content: metadata-1` with `default-provider: certbot`

#### Scenario: snapcraft.yaml exists and is valid YAML
- **WHEN** `snap/snapcraft.yaml` is parsed as YAML
- **THEN** parsing SHALL succeed AND the result SHALL be a mapping

#### Scenario: Snap metadata follows the certbot plugin convention
- **WHEN** `snap/snapcraft.yaml` is parsed
- **THEN** `name` SHALL equal `certbot-dns-arsys` AND `confinement` SHALL equal `strict` AND `grade` SHALL equal `stable` AND `base` SHALL start with `core`

#### Scenario: A python part builds the plugin from the repo
- **WHEN** `snap/snapcraft.yaml` is parsed
- **THEN** `parts` SHALL contain at least one part whose `plugin` is `python` and whose `source` is the repository root (`.`)

#### Scenario: Certbot content interface is wired
- **WHEN** `snap/snapcraft.yaml` is parsed
- **THEN** `slots` SHALL contain an entry with `interface: content` and `content: certbot-1` AND `plugs` SHALL contain a `certbot-metadata` entry with `interface: content`, `content: metadata-1`, and `default-provider: certbot`

---

### Requirement: README documents Snap installation
`README.rst` SHALL include a "Snap" section documenting how to install the plugin into the certbot snap, including the `snap install` of the plugin and the `snap connect` of the `certbot:plugin` and `certbot-dns-arsys:certbot-metadata` interfaces.

#### Scenario: Snap section present in README
- **WHEN** `README.rst` is read
- **THEN** it SHALL contain a "Snap" section heading AND reference `snap install certbot-dns-arsys` AND a `snap connect` command wiring the plugin to the certbot snap

