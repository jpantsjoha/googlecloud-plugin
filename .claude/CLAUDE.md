# GoogleCloud Plugin — Construction Guide

This file advises AI agents working ON the plugin (building, researching, validating skills).
It is committed, and public — write it for contributors, not as a scratchpad.
For local notes you don't want published, use `.claude/local-CLAUDE.md`, which is gitignored.

## Your Role

You are building a public plugin that installs a complete GCP team for other developers.
Every file you commit must be production quality — real developers will use this.

## The Split

| Location | Purpose | Committed? |
|----------|---------|-----------|
| `googlecloud-plugin/` | Public release — curated, validated | Yes (main is protected) |
| `_plugin/` | Working area — planning, research drafts, audits | No (gitignored) |

Never commit `_plugin/` content. Draft in `_plugin/staging/`, promote to `skills/` only after `make gate` passes.

## Branch Strategy

- All work on feature branches: `feat/phase-N-description`
- Main is branch-protected — PRs required
- Commit after each phase with a clear message

## Gate System (Sequential — Enforce This)

Before any skill merges to main:
1. `make gate` passes (validate + lint + test)
2. PR reviewed (join-the-team pr-reviewer or adversarial-gate for high-stakes changes)
3. Coverage matrix updated in `research/coverage-matrix.md`

## Skill Contract

Frontmatter follows the [Agent Skills specification](https://agentskills.io/specification).
The field set is **closed** — adding a top-level key outside
`{name, description, license, compatibility, allowed-tools, metadata}` makes the
skill non-conformant, and a conformant client MUST skip it. Everything specific
to this plugin is namespaced under `metadata` as **string** values:

- `name` — matches directory name exactly
- `description` — what it does AND when to use it, max 1024 chars, ending with
  `Use when the user mentions: …`. This is the only thing a conformant client
  routes on. Where two skills overlap, name the other and draw the line.
- `metadata["googlecloud-plugin/version"]`
- `metadata["googlecloud-plugin/triggers"]` — comma-joined, non-empty
- `metadata["googlecloud-plugin/required-scopes"]` — comma-joined, `""` if none
- `metadata["googlecloud-plugin/mcp-servers"]` — comma-joined, omit if none
- persona skills add `persona`, `tier`, `gate` under the same namespace

Never reintroduce a top-level `triggers`, `version` or `required_scopes` field —
that is the exact regression `make validate` exists to catch. See
[ADR-007](../architecture/decisions/ADR-007-agent-plugins-conformance.md).

Run `make spec && make validate` after any SKILL.md or manifest edit.

## Safety Rules (Non-Negotiable)

- No credential values in any file — location only
- No `--allow-unauthenticated` Cloud Run without gcp-security sign-off in HLD
- No public Cloud Storage buckets without explicit design intent
- Every billable action gets a cost warning comment before the command
- IAM: never grant `roles/owner` or `roles/editor` in skill examples

## Research Pipeline

Run `make crawl` to refresh `research/raw/` and `research/SOURCES.md`.
Run `make check` to detect URL drift.
Research output lives in `_plugin/research/` (gitignored) before being promoted to `research/raw/`.

## Architecture Docs

- HLD for every feature touching ≥2 components → `architecture/HLD/`
- LLD where HLD reveals complexity → `architecture/LLD/`
- ADRs for significant decisions → `architecture/decisions/ADR-NNN-title.md`

## Coverage Matrix

Update `research/coverage-matrix.md` whenever a skill status changes:
`missing` → `researched` → `drafted` → `normalized` → `validated`
