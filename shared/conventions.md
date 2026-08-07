# Plugin Conventions

Naming rules, structural contract, and authoring standards for all skills in this plugin.

## Skill Directory Name

Must be lowercase, hyphenated, matching the `name` field in SKILL.md frontmatter exactly.

Examples: `cloud-run`, `gcp-architect`, `logging-monitoring`

## SKILL.md Frontmatter Contract

Frontmatter must conform to the [Agent Skills specification](https://agentskills.io/specification).
The field set is **closed** — only `name`, `description`, `license`,
`compatibility`, `allowed-tools` and `metadata` are permitted. A skill carrying
any other top-level key is non-conformant, and
[Agent Plugins 1.0.0](https://agent-plugins.org/specification) §6.1 requires a
client to **skip** it. Everything specific to this plugin therefore lives under
`metadata`, namespaced.

```yaml
---
name: <matches directory name>          # 1-64 chars, lowercase, hyphens, no "--"
description: "<what it does AND when to use it — max 1024 chars>"
license: MIT
metadata:                               # map of string keys to STRING values
  "googlecloud-plugin/version": "0.1"
  "googlecloud-plugin/persona": "true"           # persona skills only
  "googlecloud-plugin/tier": "1"                 # persona skills only (1, 2, or 3)
  "googlecloud-plugin/gate": "<gate-name>"       # persona skills only
  "googlecloud-plugin/triggers": "phrase one, phrase two"
  "googlecloud-plugin/required-scopes": "service.resource.verb, ..."   # "" if none
  "googlecloud-plugin/mcp-servers": "server-id, ..."                   # omit if none
---
```

Required on every skill: `name`, `description`, and the `version`, `triggers`
and `required-scopes` metadata keys. `required-scopes` is present but empty for
non-IAM skills — the empty string is meaningful, it asserts the skill needs no
permissions.

### Writing the description

`description` is the only thing a conformant client routes on, so it carries the
weight `triggers` used to. It must say **what the skill does and when to use
it**, and end with the routing keywords: `Use when the user mentions: …`.

Where two skills have adjacent scope, each description must name the other and
draw the line — `Use this to author or change IAM; use gcp-security instead to
audit an existing posture.` Without that, both match and routing is a coin flip.

Lists in `metadata` are comma-joined strings, not YAML sequences: the spec
defines `metadata` as a map from string keys to string values. Consumers split
on `", "`.

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
