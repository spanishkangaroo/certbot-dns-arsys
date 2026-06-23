## Why

The `publish.yml` workflow already builds and publishes to PyPI via OIDC Trusted Publisher (feature #3 baseline). Two gaps remain compared with mature plugins and current supply-chain best practice:

1. A broken release can still be published — the build job does not run the test suite first.
2. Released artifacts carry no build provenance, so consumers cannot verify they were produced by this repo's CI.

## What Changes

- Gate the release: run the test suite (`pytest`) in the build job before building the distribution, so a failing test aborts the release.
- Generate signed build provenance attestations for the built `sdist` and `wheel` using `actions/attest-build-provenance`, with the required `id-token: write` and `attestations: write` permissions scoped to the build job.

## Capabilities

### New Capabilities

### Modified Capabilities

- `packaging-and-ci`: The PyPI publishing requirement is extended to require a passing test gate and build provenance attestations.

## Impact

- Changes `.github/workflows/publish.yml` only; no code or runtime impact on the plugin.
- Future releases will fail fast on broken tests and ship with verifiable provenance.
