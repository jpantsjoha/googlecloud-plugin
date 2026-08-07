# Plugin Conventions

Naming rules, structural contract, and authoring standards for all skills in this plugin.

## Skill Directory Name

Must be lowercase, hyphenated, matching the `name` field in SKILL.md frontmatter exactly.

Examples: `cloud-run`, `gcp-architect`, `logging-monitoring`

## SKILL.md Frontmatter Contract

```yaml
---
name: <matches directory name>
description: "<meaningful, >20 chars>"
version: "0.1"
persona: true          # only for persona skills (solution-designer, gcp-*)
tier: 1                # only for persona skills (1, 2, or 3)
gate: <gate-name>      # only for persona skills
license: MIT
metadata:              # Agent Skills defines metadata as string keys -> STRING values
  "googlecloud-plugin/version": "0.1"
  "googlecloud-plugin/triggers": "trigger phrase one, trigger phrase two"
  "googlecloud-plugin/required-scopes": "service.resource.verb"   # "" for non-IAM skills
  "googlecloud-plugin/mcp-servers": "server-id"                   # omit if none
---
```

The frontmatter field set is **closed**. Agent Skills permits only `name`,
`description`, `license`, `compatibility`, `metadata` and `allowed-tools`; a
skill carrying anything else is non-conformant, and Agent Plugins 1.0.0 requires
clients to skip it. Everything this plugin needs therefore lives under
`metadata`, namespaced, with lists comma-joined into strings. See
[ADR-007](../architecture/decisions/ADR-007-agent-plugins-conformance.md).

Persona skills add `"googlecloud-plugin/persona"`, `"googlecloud-plugin/tier"`
and `"googlecloud-plugin/gate"` under the same namespace.

`version`, `triggers` and `required-scopes` are required metadata keys on every
skill; `required-scopes` is emitted as `""` rather than omitted when a skill
needs no IAM scopes.

**Routing lives in `description`.** No client reads `metadata/triggers` — a
conformant client routes on the description alone, so every discriminating
keyword must appear there. Where two skills overlap, say explicitly which one
owns the case and name the other (see `gcp-ops` vs `logging-monitoring`).

## MCP Server IDs

`googlecloud-plugin/mcp-servers` names the **logical GCP capability** a skill
reaches for (`google-bigquery`, `google-gke`, …). These are not keys in
`mcp.json`. The portable `mcp.json` declares only servers that run with no
user-supplied configuration — today that is the single `gcloud` server, which
covers most of those capabilities through the `gcloud` CLI. Anything needing a
user-specific config file, such as the GenAI Toolbox and its `tools.yaml`, stays
a documented opt-in in `skills/mcp-servers/`. Do not "fix" the mismatch by
inventing server entries that cannot start.

## References Directory

Every skill must have a `references/` subdirectory. It may be empty at stub stage but must exist.

For `validated` skills, `references/` must contain at least one `.md` file linking to a live GCP doc.

## Safety Annotations

In every skill's code examples, precede billable or destructive commands with a comment:

```bash
# Billable action — confirm cost before running
gcloud ...

# Destructive — cannot be undone
gcloud ...
```

## Status Lifecycle

```
missing → researched → drafted → normalized → validated
```

- **missing**: skill does not exist yet
- **researched**: raw notes in `research/raw/<service>.md`
- **drafted**: SKILL.md exists, frontmatter valid, content may be stub
- **normalized**: content complete, references populated, `make gate` passes
- **validated**: human-reviewed, coverage matrix marked validated, indexed in `plugin.yaml`

## Authoring Rules

- All examples use placeholder values in UPPER_SNAKE_CASE (e.g. `PROJECT_ID`, `REGION`)
- No credential values in any example — paths only
- Every external URL cited must appear in `research/SOURCES.md`
- IAM examples always use least-privilege roles, never `roles/owner` or `roles/editor`
