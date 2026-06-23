## ADDED Requirements

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
