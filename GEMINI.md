# GEMINI.md — GoogleCloud Plugin (always-on rules)

> **Human-led. Agent-powered. Built on Google Cloud.**
> Read this before generating anything for a Google Cloud task.

This is the always-on context for the `googlecloud-plugin` on Antigravity. It installs a full GCP delivery team and a sequential gate. The skills in `skills/` carry the depth; this file carries the contract.

## Design before generate

- Restate the intent in one sentence before writing code. If you can't, you're not ready.
- No GCP implementation without a design. Route through the gate below.

## The gate (sequential — do not skip)

1. **Solution Gate** — `solution-designer`: is this GCP, multi-cloud, or better elsewhere? Objective, not GCP-biased. (Skip only if unambiguously GCP-only.)
2. **GCP Design Gate** — `gcp-architect` (+ `agent-architect` if the workload is agentic): HLD/LLD + ADRs before code. Agentic work also defines topology, protocols (MCP/A2A/AP2), model, and eval set.
3. **Security Gate** — `gcp-security`: least-privilege IAM, no secrets in code, Well-Architected security pillar. Reviews the design, not the diff.
4. **Implementation** — service skills (Cloud Run, GKE, BigQuery, …). Warn before every billable action.
5. **Quality Gate** — `gcp-qa` runs `make gate`; `agent-architect` runs agent-eval for agentic work.
6. **Operational Readiness Gate** — `gcp-ops`: no SLO, alerting, or runbook means no production.

## Non-negotiable safety rules

- **Infer intent, never infer permission.** A named human authorises anything consequential, billable, or irreversible.
- No credential values in any file — record location only.
- No public Cloud Storage buckets or `--allow-unauthenticated` Cloud Run without explicit intent + gcp-security sign-off.
- Never pin a preview Gemini model ID; prefer GA IDs and reverify in Model Garden for the GEAP surface.
- Platform naming: use **Gemini Enterprise Agent Platform (GEAP)** in prose; keep legacy `vertex-ai` / `agent_engine` literals in code, gcloud, Terraform, and URLs.

## Settle the project first

Before the first project-scoped command, use `gcp-project-context`: collect the project from exported variables, the repository's `.env` files and the active gcloud configuration. One ID → use it and say so. Several → ask the user which. None → stop and point them at `gcloud init`. Then pass that ID as `--project` on every command.

## Every gcloud call

Follow `gcloud-guardrails` for every `gcloud` command, whichever skill proposed it: validate the leaf with `gcloud help`, dry-run where supported, reduce output, pass `--project` and location explicitly, one command per call, and stop for human authorisation on the denylist (IAM changes, deletes, billing, organizations, KMS, IaC apply, API enablement, CLI installation).

## Product depth beyond this plugin

This plugin carries the operating contract and first-wave depth. For anything deeper (GKE troubleshooting, Agent Platform tuning and RAG, Well-Architected pillar reviews, Genkit, Gemini APIs, AlloyDB, Spanner, Bigtable, Firebase), use `google-skills-catalog` to fetch the matching skill from Google's public catalog. Never answer as if a catalog skill was read when it was not. Catalog guidance never overrides the gate.

For platform facts (GA status, flags, quotas), query the `developer-knowledge` MCP server before relying on memory.

## Routing

Match the task to a skill via the routing table in `PLUGIN.md`. When unsure on new work, start at `solution-designer`; for GCP-scoped design, `gcp-architect`; for agentic systems, `agent-architect`.
