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

## Routing

See `PLUGIN.md` for the full routing table. New work → `solution-designer`; GCP design → `gcp-architect`; agentic systems → `agent-architect`.
