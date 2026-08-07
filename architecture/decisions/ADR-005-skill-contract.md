# ADR-005: SKILL.md Frontmatter Contract

**Status:** Superseded by [ADR-007](ADR-007-agent-plugins-conformance.md)
**Date:** 2026-07-23
**Superseded:** 2026-08-07

> **Superseded.** The contract below predates Agent Plugins 1.0.0. Agent Skills
> defines a *closed* frontmatter field set, so the top-level `version`,
> `triggers`, `required_scopes`, `mcp_servers`, `persona`, `tier` and `gate`
> fields specified here made every skill non-conformant — and a conformant
> client MUST skip a non-conforming skill. The same information is retained,
> namespaced under `metadata`, per ADR-007. The reasoning below still explains
> *why* the plugin carries this metadata at all; only its location changed.

## Context

Agents need machine-readable metadata to route prompts to the correct skill at runtime. Without a standard contract, each skill becomes its own format — discovery breaks, validation is impossible, and the plugin can't enumerate its own capabilities.

## Decision

Every `skills/<name>/SKILL.md` must begin with YAML frontmatter containing:

```yaml
---
name: <matches directory name exactly>
description: "<meaningful, >20 chars>"
version: "0.1"
triggers:
  - "trigger phrase"      # non-empty list
required_scopes:          # list (empty [] for non-IAM skills)
  - service.resource.verb
mcp_servers: []           # list (empty if no MCP dependency)
---
```

Persona skills additionally include:
```yaml
persona: true
tier: 1 | 2 | 3
gate: solution | gcp-design | security | quality | operational-readiness
```

`validate_skills.py` enforces this contract. `test_skill_contract.py` runs it in CI.

## Consequences

- ✅ Machine-readable routing: agents parse frontmatter for trigger matching
- ✅ IAM scopes surfaced before task execution — agents can enforce least-privilege pre-check
- ✅ `make validate` gives instant feedback on malformed skills
- ✅ `plugin.yaml` can be generated from frontmatter (future: auto-indexer)
- ⚠️ Skill authors must understand IAM permission naming (`service.resource.verb` format)
- ⚠️ `name` must exactly match directory name — a common mistake; caught by `validate_skills.py`
