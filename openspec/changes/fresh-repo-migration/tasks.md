## 1. Repository Rename & Recreation

- [ ] 1.1 Rename current repo `spanishkangaroo/certbot-dns-arsys` → `certbot-dns-arsys-archive` via `gh repo rename`
- [ ] 1.2 Create new repo `spanishkangaroo/certbot-dns-arsys` via `gh repo create` (public, same visibility)
- [ ] 1.3 Verify new repo exists and is accessible

## 2. Content Migration

- [ ] 2.1 Remove `.git` directory from current working copy
- [ ] 2.2 `git init` fresh repository with `main` branch
- [ ] 2.3 Add all files (excluding `.git`) and create single initial commit: "Initial commit: certbot-dns-arsys plugin"
- [ ] 2.4 Set remote origin to new repo and push `main`
- [ ] 2.5 Verify all files are present on GitHub (README, source, tests, CI workflows, snap config)

## 3. GitHub Releases

- [ ] 3.1 Create tag `v0.1.0` and release with notes: "Initial release of certbot-dns-arsys — Certbot DNS authenticator plugin for Arsys domains."
- [ ] 3.2 Create tag `v0.1.1` and release with notes: "Bump version to 0.1.1"
- [ ] 3.3 Create tag `v0.1.2` and release with notes: "Lower Python requirement to >=3.10; Fix publish workflow; Document release process in AGENTS.md; Fix Python version in README"

## 4. Old Repository Cleanup

- [ ] 4.1 Archive `spanishkangaroo/certbot-dns-arsys-archive` via `gh repo edit --archive`
- [ ] 4.2 Verify old repo shows as archived (read-only, hidden from search)

## 5. External Service Verification

- [ ] 5.1 Verify PyPI Trusted Publisher: check that OIDC publish workflow will work with new repo (same owner/repo name)
- [ ] 5.2 Verify Dependabot: confirm config is carried over and will run on new repo
- [ ] 5.3 Verify Docker GHCR: confirm `${{ github.repository }}` resolves correctly for new repo
- [ ] 5.4 Verify Snap Store: confirm snapcraft.yaml is valid and snap publish workflow will work
