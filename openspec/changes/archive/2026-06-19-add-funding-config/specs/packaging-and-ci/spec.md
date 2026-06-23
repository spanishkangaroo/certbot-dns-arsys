## ADDED Requirements

### Requirement: Repository declares sponsorship via FUNDING.yml
The repository SHALL include a `.github/FUNDING.yml` file so GitHub surfaces a "Sponsor" button for the project. The file SHALL be valid YAML using GitHub's funding schema and SHALL declare at least one funding channel. It SHALL include a `github:` entry naming the maintainer `spanishkangaroo`.

#### Scenario: FUNDING.yml exists and is valid YAML
- **WHEN** `.github/FUNDING.yml` is parsed as YAML
- **THEN** parsing SHALL succeed AND the result SHALL be a mapping

#### Scenario: GitHub sponsorship channel is declared
- **WHEN** `.github/FUNDING.yml` is parsed
- **THEN** it SHALL contain a `github` key whose value names `spanishkangaroo` (as a string or within a list)

#### Scenario: Only recognized funding platform keys are used
- **WHEN** `.github/FUNDING.yml` is parsed
- **THEN** every top-level key SHALL be one of GitHub's recognized funding platforms (e.g. `github`, `patreon`, `open_collective`, `ko_fi`, `tidelift`, `community_bridge`, `liberapay`, `issuehunt`, `lfx_membership`, `polar`, `buy_me_a_coffee`, `thanks_dev`, `custom`)
