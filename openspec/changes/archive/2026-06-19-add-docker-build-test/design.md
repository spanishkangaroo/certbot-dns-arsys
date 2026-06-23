## Context

The existing `docker.yml` is release-triggered and pushes to GHCR. The `Dockerfile` is `FROM certbot/certbot:latest`, copies the source, `pip install`s it, and sets `ENTRYPOINT ["certbot"]`. We want an early, push-free verification.

## Decisions

- **Separate workflow**: add `docker-build.yml` rather than overloading the release-only `docker.yml`, keeping each workflow single-purpose.
- **Build action**: use `docker/build-push-action@v6` with `push: false` and `load: true` so the built image is available to the Docker daemon for the verification step.
- **Verification**: `docker run --rm <image> plugins` (the entrypoint is `certbot`, so this runs `certbot plugins`) piped to `grep dns-arsys`, which exits non-zero if the plugin is missing.
- **Triggers**: `push` and `pull_request` to mirror `test.yml`.

## Risks / Trade-offs

- Building from `certbot/certbot:latest` pulls a base image each run; build time is a minute or two — acceptable for the regression coverage gained.
- Using `:latest` base means the build can break if upstream changes; that is exactly the kind of breakage this workflow surfaces early.
