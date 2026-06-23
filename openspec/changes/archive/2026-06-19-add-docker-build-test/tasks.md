## 1. Add Docker build-test workflow

- [x] 1.1 Create `.github/workflows/docker-build.yml` triggered on `push` and `pull_request`
- [x] 1.2 Build the image with `docker/build-push-action@v6` (`push: false`, `load: true`, a local tag)
- [x] 1.3 Add a step running `certbot plugins` inside the image and asserting `dns-arsys` is listed

## 2. Validate

- [x] 2.1 Confirm `docker-build.yml` is valid YAML
- [x] 2.2 Verify locally that `docker build` succeeds and `docker run <image> plugins` lists `dns-arsys`
- [x] 2.3 Run `openspec validate add-docker-build-test --strict` and resolve any issues
