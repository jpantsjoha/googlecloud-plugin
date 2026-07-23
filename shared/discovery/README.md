# Skill Discovery

How agents enumerate available skills at runtime.

## Primary: plugin.yaml

`plugin.yaml` at the repo root is the authoritative skill index. It lists:
- All persona skills (with tier and gate)
- All service skills (with wave and status)
- All MCP server configurations

An agent installing this plugin reads `plugin.yaml` to discover what's available.

## Secondary: PLUGIN.md routing table

`PLUGIN.md` contains a human-readable routing table mapping trigger phrases to skills.
Agents can use this for fuzzy routing when an exact skill name is not known.

## Filesystem

Skills are always at `skills/<name>/SKILL.md`. An agent can enumerate all skills by listing `skills/*/SKILL.md`.

## Skill Status Filter

Agents should only route to skills with `status: normalized` or `status: validated` in `plugin.yaml`.
Skills with `status: stub` or `status: drafted` are in-progress and may be incomplete.

## Coverage Matrix

`research/coverage-matrix.md` shows the current status of every first-wave service.
Consult this before assuming a skill is production-ready.
