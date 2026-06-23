## Why

Certbot is very commonly installed as a strictly-confined snap, and a pip-installed plugin is invisible to a snap-installed certbot (the project's own Troubleshooting section already calls this out). Without a snap, snap-certbot users cannot use `dns-arsys` at all. Shipping a snap recipe is the ecosystem-standard way to support these users (Feature #11 "Snap support" in `docs/dns-plugins-research.md`, found in standalone, azure, bunny, duckdns, porkbun, multi, and others).

## What Changes

- Add a `snap/snapcraft.yaml` recipe following the canonical certbot DNS plugin pattern: strict confinement, stable grade, a `python` plugin part building the package from the repo, and the certbot content-interface wiring (a `certbot` content slot exposing the plugin's site-packages plus a `certbot-metadata` content plug with `default-provider: certbot`).
- Add a "Snap" installation section to `README.rst` documenting `snap install` and `snap connect` of the plugin into the certbot snap.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `packaging-and-ci`: Add a requirement that the repository ships a valid `snap/snapcraft.yaml` enabling the plugin to be installed into the certbot snap, and that the README documents the snap install flow.

## Impact

- New file: `snap/snapcraft.yaml`.
- Modified file: `README.rst` (new "Snap" section).
- No runtime, Python code, or dependency changes. Snap **building and store publishing are out of scope** for this change (publishing requires Snap Store credentials); only the recipe and docs are added. Verification is a lightweight schema-validation test, not an actual snap build.
