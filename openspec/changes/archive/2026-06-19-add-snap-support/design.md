## Context

Certbot snaps are strictly confined; plugins must be separate snaps that connect to the certbot snap through two content interfaces:
- `certbot:plugin` — the certbot snap reads the plugin's installed Python packages.
- `certbot-dns-arsys:certbot-metadata` — the plugin reads certbot's metadata, with `default-provider: certbot` so it auto-connects.

This is a well-established, copy-pasted pattern across the certbot DNS plugin ecosystem. The deliverable here is the recipe and docs; building and publishing the snap (which need a snapcraft toolchain and Snap Store credentials) are out of scope.

## Goals / Non-Goals

**Goals:**
- Ship a coherent `snap/snapcraft.yaml` matching the certbot plugin convention.
- Document the snap install/connect flow in the README.
- Guard the recipe's structure with a CI-safe schema-validation test.

**Non-Goals:**
- Running `snapcraft` or building a `.snap` in CI (heavy, needs LXD/multipass — the "friction" the research doc flags).
- Publishing to the Snap Store or adding a publish workflow (needs `SNAPCRAFT_STORE_CREDENTIALS`).
- Adding a Snap Store badge (the snap is not published yet).

## Decisions

- **Validate via YAML-schema unit test, not a build.** Rationale: keeps CI fast and green without LXD or store secrets, while still catching typos in the interface wiring that would silently break the snap. Alternative: `snapcore/action-build` in CI — rejected for now due to runtime cost and flakiness; can be added later once publishing is set up.
- **`base: core22`.** Rationale: a current, supported base. The exact base only matters at real build/connect time against the live certbot snap; the validation test asserts `base` starts with `core` rather than pinning a value, so the recipe can be retargeted without a spec change.
- **Use `adopt-info`/`override-pull` to derive the version from `pyproject.toml`.** Rationale: single source of truth for the version; avoids drift between the package version and the snap version.
- **Keep `pyyaml` (already a dev dep from the funding change) for the test.** No new dependencies.

## Risks / Trade-offs

- [Recipe never actually built in CI, so a real `snapcraft` error could slip through] → Mitigated by following the canonical upstream template closely and validating structure; full build verification is deferred to when publishing is set up.
- [`base`/python version may not match the live certbot snap at connect time] → The snap is not published here, so no user is affected yet; the base can be tuned before any real publish. The test deliberately does not pin the base.
- [README `snap connect` command names must match the snap/interface names] → The validation test asserts the README references `snap install certbot-dns-arsys` and a `snap connect`, keeping docs and recipe loosely in sync.
