## Context

Dependabot is configured declaratively in `.github/dependabot.yml` (schema `version: 2`). The repo has Python dependencies in `pyproject.toml` and GitHub Actions in `.github/workflows/`.

## Decisions

- **Ecosystems**: `pip` (covers `pyproject.toml` dependencies) and `github-actions`.
- **Schedule**: `weekly` for both — enough to stay current without PR noise on a small plugin.
- **Directory**: `/` for both ecosystems (pyproject and workflows live at the repo root / standard `.github` path).
- **Open PR limit**: leave at the Dependabot default; no custom limits needed for a small project.

## Risks / Trade-offs

- Dependabot only runs on the default branch of the GitHub repository once merged; it has no effect in CI on the PR branch. Validation is therefore limited to YAML well-formedness and schema-shape checks.
