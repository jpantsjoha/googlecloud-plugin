# GoogleCloud Plugin — Construction Guide

This file advises AI agents working ON the plugin (building, researching, validating skills).
It is gitignored and never committed to the public repo.

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

The frontmatter field set is **closed** by the Agent Skills specification. Only
`name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools`
are permitted — a skill carrying anything else is non-conformant, and Agent
Plugins 1.0.0 requires clients to **skip** it. Never add a top-level field.

Every `skills/<name>/SKILL.md` must have:
- `name` — matches directory name exactly, lowercase, no `--`
- `description` — meaningful, ≤1024 chars, **and carries every routing keyword**
- `license`
- `metadata` — string keys to **string** values, all namespaced
  `googlecloud-plugin/…`. Required: `version`, `triggers`, `required-scopes`
  (emit `""`, don't omit, when a skill needs no IAM scopes). Personas add
  `persona`, `tier`, `gate`. Lists are comma-joined.

**Routing lives in the description.** No client reads `metadata/triggers` — it is
an index for this repo's own tooling, and `make validate` fails if any trigger is
missing from the description. When two skills overlap, state in each description
which one owns the case and name the other.

Run `make validate` after any SKILL.md edit, and `make spec` after touching
`plugin.json` or `mcp.json`. See
`architecture/decisions/ADR-007-agent-plugins-conformance.md`.

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
