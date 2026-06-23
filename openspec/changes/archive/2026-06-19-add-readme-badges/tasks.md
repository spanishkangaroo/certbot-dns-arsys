## 1. Add badges to README

- [x] 1.1 Insert a block of RST `.. image::` badge directives (PyPI version, license, Python versions, CI status) directly under the title in `README.rst`, each with `:target:` and `:alt:`
- [x] 1.2 Verify the RST renders without errors (`python -m docutils README.rst /dev/null` or `python -m readme_renderer`/`twine check` if available)

## 2. Validate

- [x] 2.1 Run `openspec validate add-readme-badges --strict` and resolve any issues
- [x] 2.2 Confirm existing test suite still passes (`pytest tests/`)
