## Context

The repository currently has no GitHub funding metadata. GitHub reads `.github/FUNDING.yml` to render a "Sponsor" button. The maintainer's GitHub handle is `spanishkangaroo`. This is a documentation/community-metadata change with no runtime impact.

## Goals / Non-Goals

**Goals:**
- Add a valid `.github/FUNDING.yml` declaring a GitHub Sponsors channel for `spanishkangaroo`.
- Verify the file is valid against GitHub's funding schema in the test suite so it cannot silently break.

**Non-Goals:**
- Setting up payment platforms other than GitHub Sponsors.
- Adding `custom:` URLs or third-party platforms (can be added later without spec changes).

## Decisions

- **Use only the `github:` key.** Rationale: it is the canonical GitHub-native channel, requires no external account configuration in the repo, and avoids dead links. Alternative considered: adding `ko_fi`/`buy_me_a_coffee` — rejected for now since those accounts may not exist and would surface broken links.
- **Validate via a unit test rather than relying on GitHub alone.** Rationale: GitHub silently ignores an invalid FUNDING.yml; a test that parses the YAML and asserts the schema keeps it correct. Alternative: no test — rejected because the research feature's value is the working Sponsor button, and a silent typo would defeat it.

## Risks / Trade-offs

- [GitHub handle is wrong/not enrolled in Sponsors] → The button simply won't appear; no breakage. The handle `spanishkangaroo` matches the repository owner, minimizing risk.
- [Recognized-platform list drifts as GitHub adds platforms] → The test only asserts keys are within a known allow-list of current platforms; if GitHub adds new ones, the test can be updated. Low likelihood of impact for a single `github:` entry.
