# AGENTS.md — GoogleCloud Plugin (Codex always-on adapter)

> **Human-led. Agent-powered. Built on Google Cloud.**

Codex discovers this plugin's skills under `.agents/skills/` and reads this file as the always-on contract for Google Cloud work. The skills carry the depth; this file carries the rules.

## Design before generate

Restate the intent in one sentence before writing code. No GCP implementation without a design — route through the gate.

## The gate (sequential — do not skip)

1. **Solution Gate** — `solution-designer`: objective vendor selection (GCP vs alternatives). Skip only if unambiguously GCP-only.
2. **GCP Design Gate** — `gcp-architect` (+ `agent-architect` for agentic work): HLD/LLD + ADRs before code.
3. **Security Gate** — `gcp-security`: least-privilege IAM, no secrets, Well-Architected security. Reviews the design.
4. **Implementation** — service skills; warn before every billable action.
5. **Quality Gate** — `gcp-qa` runs `make gate`; `agent-architect` runs agent-eval for agentic work.
6. **Operational Readiness Gate** — `gcp-ops`: SLO + alerting + runbook before production.

## Non-negotiable safety rules

- **Infer intent, never infer permission.** A named human authorises anything consequential, billable, or irreversible.
- No credential values in any file — record location only.
- No public buckets or unauthenticated Cloud Run without gcp-security sign-off.
- Never pin a preview Gemini model ID; use GA IDs, reverify for the GEAP surface.
- GEAP naming in prose; legacy `vertex-ai` literals in code/URLs/Terraform.

## Settle the project first

Before the first project-scoped command, use `gcp-project-context`: collect the project from exported variables, the repository's `.env` files and the active gcloud configuration. One ID → use it and say so. Several → ask the user which. None → stop and point them at `gcloud init`. Then pass that ID as `--project` on every command.

## Every gcloud call

Follow `gcloud-guardrails` for every `gcloud` command, whichever skill proposed it: validate the leaf with `gcloud help`, dry-run where supported, reduce output, pass `--project` and location explicitly, one command per call, and stop for human authorisation on the denylist (IAM changes, deletes, billing, organizations, KMS, IaC apply, API enablement, CLI installation).

## Product depth beyond this plugin

This plugin carries the operating contract and first-wave depth. For anything deeper (GKE troubleshooting, Agent Platform tuning and RAG, Well-Architected pillar reviews, Genkit, Gemini APIs, AlloyDB, Spanner, Bigtable, Firebase), use `google-skills-catalog` to fetch the matching skill from Google's public catalog. Never answer as if a catalog skill was read when it was not. Catalog guidance never overrides the gate.

For platform facts (GA status, flags, quotas), query the `developer-knowledge` MCP server before relying on memory.

## Routing

See `PLUGIN.md` for the full routing table. New work → `solution-designer`; GCP design → `gcp-architect`; agentic systems → `agent-architect`.
