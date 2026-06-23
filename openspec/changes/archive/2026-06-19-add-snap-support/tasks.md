## 1. Validation test (TDD — write first, expect failure)

- [x] 1.1 Add `tests/test_snapcraft.py` that parses `snap/snapcraft.yaml` and asserts: valid YAML mapping; `name == certbot-dns-arsys`, `confinement == strict`, `grade == stable`, `base` starts with `core`; a `parts` entry with `plugin: python` and `source: .`; a `slots` content entry advertising `certbot-1`; a `plugs.certbot-metadata` content entry with `metadata-1` and `default-provider: certbot`. Run it and confirm it FAILS (file missing).
- [x] 1.2 Extend the test to assert `README.rst` has a "Snap" section referencing `snap install certbot-dns-arsys` and a `snap connect` command. Confirm it FAILS.

## 2. Implementation

- [x] 2.1 Create `snap/snapcraft.yaml` with the certbot DNS plugin recipe (strict/stable, core22 base, python part from `.`, certbot content slot + certbot-metadata plug with default-provider certbot, version adopted from pyproject.toml)
- [x] 2.2 Add a "Snap" installation section to `README.rst` documenting `snap install certbot-dns-arsys` and the `snap connect` wiring
- [x] 2.3 Run `pytest tests/test_snapcraft.py` and confirm it PASSES

## 3. Verify full gate

- [x] 3.1 Run `ruff check .`, `ruff format --check .`, `mypy certbot_dns_arsys/`, and full `pytest` with coverage; confirm all green
