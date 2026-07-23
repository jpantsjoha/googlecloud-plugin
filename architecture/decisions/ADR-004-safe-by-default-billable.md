# ADR-004: Safe-by-Default for Billable Actions

**Status:** Accepted  
**Date:** 2026-07-23

## Context

GCP charges for compute, storage, queries, and egress. An AI agent executing a BigQuery query on a multi-TB table or deploying a GPU endpoint can incur unexpected cost. Developers (and agents) need a consistent safety mechanism.

## Decision

Every billable action in any skill must:
1. Precede the command with a comment: `# Billable action — confirm cost before running`
2. Where available, show a dry-run equivalent before the live command
3. For BigQuery: always show `--dry_run` before the live query
4. For destructive actions: precede with `# Destructive — cannot be undone`
5. Agents executing on behalf of a user must surface the cost warning and pause for confirmation

## Consequences

- ✅ Accidental cost spikes prevented
- ✅ Consistent safety signal across all 16 skills
- ✅ Dry-run patterns teach good habits alongside the skill
- ⚠️ Slightly more verbose examples — acceptable cost for safety
- ⚠️ Cost estimate accuracy depends on GCP pricing API; where unknown, warn generically
