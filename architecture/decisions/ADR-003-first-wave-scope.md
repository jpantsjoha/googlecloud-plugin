# ADR-003: First-Wave Service Scope (v0.1)

**Status:** Accepted  
**Date:** 2026-07-23

## Context

Google Cloud has 200+ services. Attempting full coverage before v0.1 is indefinite. The plugin needs credibility at launch — zero missing, zero stale for the services it claims to cover.

## Decision

v0.1 targets **8 first-wave services** plus 5 personas, 3 cross-cutting skills:

**First wave:** Cloud Run, GKE, IAM, BigQuery, Cloud Storage, Vertex AI, Networking, Logging/Monitoring

**Personas:** solution-designer, gcp-architect, gcp-security, gcp-ops, gcp-qa

**Cross-cutting:** mcp-servers, well-architected, terraform-gcp

Second wave (Pub/Sub, Cloud Functions, Cloud SQL, Spanner, Dataflow, BigTable, Firebase, etc.) targets v0.2 after v0.1 validation.

## Consequences

- ✅ Achievable: 8 services + 5 personas + 3 cross-cutting = 16 skills (done in Phase 0)
- ✅ Coverage is credible: these services are used by most GCP workloads
- ✅ Quality bar is clear: zero missing, zero stale for listed services at v0.1
- ⚠️ Users needing second-wave services must wait for v0.2 or contribute a skill PR
- ⚠️ Roadmap must be transparent — `coverage-matrix.md` shows second-wave as `missing`
