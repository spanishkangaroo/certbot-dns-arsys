## Context

`publish.yml` has two jobs: `build` (checkout, setup-python, install build, `python -m build`, upload artifact) and `publish` (download artifact, `pypa/gh-action-pypi-publish` with `id-token: write`). The plugin's dev dependencies and tests are already defined and run in `test.yml`.

## Decisions

- **Test gate location**: run tests inside the `build` job (install `.[dev]`, then `pytest`) rather than as a separate `needs` job, keeping the release pipeline a single linear path and avoiding a second checkout/setup.
- **Attestation action**: use `actions/attest-build-provenance@v1`, which integrates with GitHub's attestation store and Sigstore. It runs after `python -m build`, pointing at `dist/*`.
- **Permissions**: the `build` job gains `id-token: write` (OIDC for the attestation) and `attestations: write` (to record the attestation), plus the default `contents: read`. The `publish` job keeps its own `id-token: write` for Trusted Publishing.

## Risks / Trade-offs

- The workflow only runs on a real tag push, so these changes cannot be exercised by PR CI; correctness is verified by YAML/action-shape review and by the unchanged `test.yml` continuing to pass.
- Adding the test gate lengthens release time slightly — acceptable for the safety it provides.
