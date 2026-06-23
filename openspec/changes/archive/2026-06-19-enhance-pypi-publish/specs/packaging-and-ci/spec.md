## MODIFIED Requirements

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
