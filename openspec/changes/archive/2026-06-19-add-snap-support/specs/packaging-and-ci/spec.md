## ADDED Requirements

### Requirement: Plugin ships a Snap recipe for the certbot snap
The repository SHALL include a `snap/snapcraft.yaml` that builds `certbot-dns-arsys` as a strictly-confined snap installable into the certbot snap. The recipe SHALL:
- declare `name: certbot-dns-arsys`, `confinement: strict`, and `grade: stable`
- declare a `base` (a `core*` base such as `core20`/`core22`/`core24`)
- build the plugin via a `parts` entry using the `python` plugin sourced from the repository root
- expose the plugin to certbot through the content interface: a `slots` entry of `interface: content` advertising `content: certbot-1`, and a `plugs` entry `certbot-metadata` of `interface: content` advertising `content: metadata-1` with `default-provider: certbot`

#### Scenario: snapcraft.yaml exists and is valid YAML
- **WHEN** `snap/snapcraft.yaml` is parsed as YAML
- **THEN** parsing SHALL succeed AND the result SHALL be a mapping

#### Scenario: Snap metadata follows the certbot plugin convention
- **WHEN** `snap/snapcraft.yaml` is parsed
- **THEN** `name` SHALL equal `certbot-dns-arsys` AND `confinement` SHALL equal `strict` AND `grade` SHALL equal `stable` AND `base` SHALL start with `core`

#### Scenario: A python part builds the plugin from the repo
- **WHEN** `snap/snapcraft.yaml` is parsed
- **THEN** `parts` SHALL contain at least one part whose `plugin` is `python` and whose `source` is the repository root (`.`)

#### Scenario: Certbot content interface is wired
- **WHEN** `snap/snapcraft.yaml` is parsed
- **THEN** `slots` SHALL contain an entry with `interface: content` and `content: certbot-1` AND `plugs` SHALL contain a `certbot-metadata` entry with `interface: content`, `content: metadata-1`, and `default-provider: certbot`

### Requirement: README documents Snap installation
`README.rst` SHALL include a "Snap" section documenting how to install the plugin into the certbot snap, including the `snap install` of the plugin and the `snap connect` of the `certbot:plugin` and `certbot-dns-arsys:certbot-metadata` interfaces.

#### Scenario: Snap section present in README
- **WHEN** `README.rst` is read
- **THEN** it SHALL contain a "Snap" section heading AND reference `snap install certbot-dns-arsys` AND a `snap connect` command wiring the plugin to the certbot snap
