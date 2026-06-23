## 1. Add test gate to publish workflow

- [x] 1.1 In `publish.yml` build job, install dev dependencies (`pip install -e ".[dev]"`) and run `pytest tests/` before `python -m build`

## 2. Add build provenance attestation

- [x] 2.1 Add `id-token: write` and `attestations: write` permissions to the build job
- [x] 2.2 After building, add an `actions/attest-build-provenance@v1` step targeting `dist/*`

## 3. Validate

- [x] 3.1 Confirm `publish.yml` is valid YAML
- [x] 3.2 Run `openspec validate enhance-pypi-publish --strict` and resolve any issues
- [x] 3.3 Confirm existing test suite still passes (`pytest tests/`)
