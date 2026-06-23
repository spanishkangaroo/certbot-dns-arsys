## Why

A Docker image and a release-time build/push workflow already exist (feature #5 baseline), but the `Dockerfile` is only built when a release is published. A broken `Dockerfile` (or a change that stops the plugin from registering) is not caught until release time. Plugins like duckdns and porkbun run a Docker build test in CI to catch this on every change.

## What Changes

- Add a `docker-build.yml` workflow triggered on `push` and `pull_request` that:
  - Builds the image from the project `Dockerfile` without pushing.
  - Runs `certbot plugins` inside the freshly built image and asserts `dns-arsys` is registered.

## Capabilities

### New Capabilities

### Modified Capabilities

- `packaging-and-ci`: A new requirement is added for verifying the Docker image build (and plugin registration) in CI on every push and PR.

## Impact

- Adds one workflow file; no code or runtime impact on the plugin.
- Dockerfile regressions are caught on PRs instead of at release time.
