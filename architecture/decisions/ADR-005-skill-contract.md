# ADR-005: SKILL.md Frontmatter Contract

**Status:** Accepted  
**Date:** 2026-07-23

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
