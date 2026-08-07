# ADR-005: SKILL.md Frontmatter Contract

**Status:** Superseded by [ADR-007](ADR-007-agent-plugins-conformance.md) (2026-08-07)
**Date:** 2026-07-23

> **Superseded.** The frontmatter shape below is non-conformant with the Agent
> Skills specification, whose field set is closed. `version`, `triggers`,
> `required_scopes`, `mcp_servers`, `persona`, `tier`, `gate` and `owns_eval`
> are not permitted at the top level, and Agent Plugins 1.0.0 requires clients
> to **skip** any skill that carries them — all 17 skills, in practice.
>
> The contract itself survives; only its location changed. Every field below now
> lives under `metadata` as a namespaced string value, and routing keywords fold
> into `description`. See ADR-007 for the current shape and the reasoning.
>
> Retained for the record: the *motivation* below still holds, and the gate
> discipline it established is what made the drift detectable.

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
