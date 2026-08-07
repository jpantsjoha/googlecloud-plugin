# Coverage Matrix

Tracks skill status for every first-wave service. Update whenever a skill progresses.

**Status values:** `missing` → `researched` → `drafted` → `normalized` → `validated`

**v0.1 target:** All first-wave services at `validated` before release tag.

**v0.2 target:** every skill conformant with the [Agent Skills specification](https://agentskills.io/specification)
and discoverable under [Agent Plugins 1.0.0](https://agent-plugins.org/specification) — met at v0.2.0
(17/17 valid per the upstream `skills-ref` reference validator).

Last updated: 2026-08-07 (v0.2.0 — Agent Plugins 1.0.0 conformance; 17/17 skills valid, 102 URLs resolve, gate green)

---

## Personas

| Persona | Skill | Status | Notes |
|---------|-------|--------|-------|
| Solution Designer | `skills/solution-designer/` | normalized | Frontmatter valid, references live, gate green |
| GCP Architect | `skills/gcp-architect/` | normalized | Frontmatter valid, references live, gate green |
| Agent Architect | `skills/agent-architect/` | normalized | Tier 2 agentic specialist; owns agent-eval; references live, gate green |
| GCP Security | `skills/gcp-security/` | normalized | Frontmatter valid, references live, gate green |
| GCP Ops | `skills/gcp-ops/` | normalized | Frontmatter valid, references live, gate green |
| GCP QA | `skills/gcp-qa/` | normalized | Frontmatter valid, references live, gate green |

## First-Wave Service Skills

| Service | Skill | Status | Research | Notes |
|---------|-------|--------|----------|-------|
| Cloud Run | `skills/cloud-run/` | normalized | complete | References live, gate green |
| GKE | `skills/gke/` | normalized | complete | References live, gate green |
| IAM | `skills/iam/` | normalized | complete | References live, gate green |
| BigQuery | `skills/bigquery/` | normalized | complete | References live, gate green |
| Cloud Storage | `skills/cloud-storage/` | normalized | complete | References live, gate green |
| Vertex AI | `skills/vertex-ai/` | normalized | complete | References live, gate green |
| Networking | `skills/networking/` | normalized | complete | References live, gate green |
| Logging/Monitoring | `skills/logging-monitoring/` | normalized | complete | References live, gate green |

## Cross-Cutting Skills

| Service | Skill | Status | Notes |
|---------|-------|--------|-------|
| MCP Servers | `skills/mcp-servers/` | normalized | References live, gate green |
| Well-Architected | `skills/well-architected/` | normalized | All 6 pillars, references live |
| Terraform GCP | `skills/terraform-gcp/` | normalized | CFT + google provider, references live |

## Second-Wave (v0.2 — not in scope for v0.1)

| Service | Status |
|---------|--------|
| Pub/Sub | missing |
| Cloud Functions | missing |
| Cloud Spanner | missing |
| Dataflow | missing |
| BigTable | missing |
| Dataproc | missing |
| Firebase | missing |
| Cloud SQL | missing |
| Secret Manager | missing |
| Artifact Registry | missing |
