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
triggers:
  - "trigger phrase one"
  - "trigger phrase two"
required_scopes:       # list of GCP IAM permission strings (empty list [] for non-IAM skills)
  - service.resource.verb
mcp_servers:           # list of MCP server IDs this skill uses (empty list [] if none)
  - server-id
---
```

All fields except `persona`, `tier`, and `gate` are required on every skill.

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
