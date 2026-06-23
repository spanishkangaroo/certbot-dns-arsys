## Context

`README.rst` is reStructuredText (renders on both GitHub and PyPI). Badges must use RST `.. image::` directives with `:target:` and `:alt:` options, placed after the title underline and before the description paragraph.

## Decisions

- **Badge source**: use [shields.io](https://shields.io) dynamic badges so they stay current without manual updates:
  - PyPI version: `https://img.shields.io/pypi/v/certbot-dns-arsys`
  - License: `https://img.shields.io/pypi/l/certbot-dns-arsys`
  - Python versions: `https://img.shields.io/pypi/pyversions/certbot-dns-arsys`
  - CI status: `https://github.com/spanishkangaroo/certbot-dns-arsys/actions/workflows/test.yml/badge.svg`
- **Repository slug**: the GitHub remote is `spanishkangaroo/certbot-dns-arsys`; badge/target URLs use that slug.
- **Placement**: a single block of `.. image::` directives directly under the title, separated from the description by a blank line, so RST renders them on one line.

## Risks / Trade-offs

- PyPI-sourced badges will show "not found" until the package is published; acceptable because publish automation already exists and badges self-heal once the release lands.
