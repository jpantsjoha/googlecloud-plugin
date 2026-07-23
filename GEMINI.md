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

## Routing

Match the task to a skill via the routing table in `PLUGIN.md`. When unsure on new work, start at `solution-designer`; for GCP-scoped design, `gcp-architect`; for agentic systems, `agent-architect`.
