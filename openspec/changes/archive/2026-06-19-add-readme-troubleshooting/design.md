## Context

`README.rst` is reStructuredText. It currently has a "Notes" section near the end covering the non-standard port and propagation timing. The Troubleshooting section should consolidate and expand actionable guidance without duplicating the Notes content.

## Decisions

- **Placement**: insert the `Troubleshooting` section after `Options` and before the existing `Notes` section, so problem-solving guidance sits close to usage.
- **Format**: use RST subsection headings (a problem statement per item) with `code-block`/literal commands where a concrete check helps (e.g. `certbot plugins`, an `openssl`/`nc` connectivity probe, `chmod 600`).
- **Scope**: cover the five failure modes from the spec; reference `--dns-arsys-propagation-seconds` for timeouts and the port 54321 firewall requirement for connectivity.

## Risks / Trade-offs

- Mild overlap with the existing Notes section (port, propagation). Acceptable: Notes stays as background context; Troubleshooting gives the actionable fix. The verification step confirms RST still renders cleanly.
