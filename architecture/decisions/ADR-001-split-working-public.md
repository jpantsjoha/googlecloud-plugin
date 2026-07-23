# ADR-001: Split Working / Public Directories

**Status:** Accepted  
**Date:** 2026-07-23

## Context

Plugin construction produces research, drafts, rejected candidates, planning documents, and audit reports alongside the final curated skills. Committing all of this to main exposes unvalidated content to plugin consumers.

## Decision

Two locations with distinct gitignore treatment:
- `googlecloud-plugin/` (public) — curated, peer-reviewed, quality-gated skills only
- `_plugin/` (gitignored) — all planning, research output, draft skills, audits, roadmaps

Skills graduate from `_plugin/staging/` to `skills/` only after passing `make gate`.

## Consequences

- ✅ Public repo stays clean; consumers only install stable, validated content
- ✅ Builders have a workspace to draft and experiment without risk of broken releases
- ✅ The quality gate (draft → review → public release) is enforced structurally, not by convention
- ⚠️ `.gitignore` must explicitly list `_plugin/` — accidental git add is the risk
