---
name: googlecloud-plugin
description: "Unified Google Cloud plugin. Installs a full operational GCP team: vendor-agnostic solution designer, GCP architect, security enforcer, SRE/ops, and QA — plus 11 service skills and MCP server configurations. Design-first, security-first, Well-Architected aligned."
version: "0.1.0"
---

# GoogleCloud Plugin

One plugin. Full Google Cloud capability.

Installs 5 personas + 11 service skills + MCP server configurations. All work flows through sequential quality gates. Design before code. Security before implementation. Evidence before release.

---

## Routing Table

Route agent prompts to the correct skill using the trigger list below. When in doubt, start with `solution-designer` for new work or `gcp-architect` for GCP-scoped design.

### Tier 1 — Solution Authority

| Trigger Pattern | Skill |
|----------------|-------|
| Multi-vendor, multi-cloud, which-cloud, cross-cloud, overarching design | `skills/solution-designer/` |
| Vendor comparison, objective architecture, hybrid cloud | `skills/solution-designer/` |

### Tier 2 — GCP Domain Architecture

| Trigger Pattern | Skill |
|----------------|-------|
| GCP HLD, GCP design, architect on GCP, GCP ADR | `skills/gcp-architect/` |
| Well-Architected Framework review, GCP pillars | `skills/well-architected/` |
| Terraform on GCP, IaC GCP, CFT, landing zone | `skills/terraform-gcp/` |

### Tier 3 — Delivery + Assurance

| Trigger Pattern | Skill |
|----------------|-------|
| Security review, IAM review, secrets, least-privilege | `skills/gcp-security/` |
| Monitoring, alerting, SLO, runbook, observability | `skills/gcp-ops/` |
| QA, validate, lint, smoke test, release check | `skills/gcp-qa/` |

### Service Skills

| Trigger Pattern | Skill |
|----------------|-------|
| Cloud Run, serverless container, deploy container | `skills/cloud-run/` |
| GKE, Kubernetes, GKE cluster, node pool | `skills/gke/` |
| IAM policy, service account, roles, grant access | `skills/iam/` |
| BigQuery, BQ query, dataset, analytics GCP | `skills/bigquery/` |
| Cloud Storage, GCS, bucket, object storage | `skills/cloud-storage/` |
| Vertex AI, Gemini GCP, model, endpoint, agent builder | `skills/vertex-ai/` |
| VPC, firewall, load balancer, networking GCP | `skills/networking/` |
| Cloud Logging, Cloud Monitoring, alerting, trace | `skills/logging-monitoring/` |

### Cross-Cutting

| Trigger Pattern | Skill |
|----------------|-------|
| MCP server, MCP setup, GenAI Toolbox | `skills/mcp-servers/` |

---

## Gate System (Sequential — Non-Negotiable)

```
New work or feature request
    ↓
[SOLUTION GATE] solution-designer
    Skip if: unambiguously GCP-only, no cross-vendor components
    ↓
[GCP DESIGN GATE] gcp-architect
    Block if: no GCP HLD, or HLD contradicts solution design
    ↓
[SECURITY GATE] gcp-security
    Block if: IAM over-permissive, secrets in code, GCP risks unaddressed
    ↓
[IMPLEMENTATION] service skills
    Warn before every billable action
    ↓
[QUALITY GATE] gcp-qa  →  make gate
    Block if: validate/lint/test fails, acceptance criteria unmet
    ↓
[OPERATIONAL READINESS GATE] gcp-ops
    Block if: no SLO, no alerting, no runbook for production workload
    ↓
Release
```

---

## Validation (3-Minute Gate)

```bash
make gate       # validate + lint + test — must pass before any merge to main
make validate   # SKILL.md frontmatter contract
make lint       # reference URL liveness
make test       # pytest smoke tests
make check      # freshness: hash drift detection
make crawl      # research pipeline (weekly)
```

---

## Plugin Structure

```
googlecloud-plugin/
├── PLUGIN.md               # This file — top-level orchestrator
├── plugin.yaml             # Metadata, version, full skill index
├── Makefile                # Validation targets (make gate)
├── skills/                 # All skill folders
│   ├── solution-designer/  # Tier 1: vendor-agnostic
│   ├── gcp-architect/      # Tier 2: GCP design authority
│   ├── gcp-security/       # Tier 3: security gate
│   ├── gcp-ops/            # Tier 3: SRE / ops
│   ├── gcp-qa/             # Tier 3: quality gate
│   ├── cloud-run/          # Service skill
│   ├── gke/                # Service skill
│   ├── iam/                # Service skill
│   ├── bigquery/           # Service skill
│   ├── cloud-storage/      # Service skill
│   ├── vertex-ai/          # Service skill
│   ├── networking/         # Service skill
│   ├── logging-monitoring/ # Service skill
│   ├── mcp-servers/        # MCP configuration + setup
│   ├── well-architected/   # GCP WAF reference
│   └── terraform-gcp/      # IaC patterns
├── architecture/
│   ├── HLD/                # High-level designs
│   ├── LLD/                # Low-level designs
│   ├── decisions/          # ADRs (ADR-001 onward)
│   └── patterns/           # Reusable GCP patterns
├── engineering/
│   ├── features/           # Feature implementation docs
│   ├── use-cases/          # Business use case definitions
│   └── runbooks/           # Operational runbooks
├── shared/
│   ├── auth/               # ADC + SA patterns
│   └── discovery/          # Agent skill enumeration
├── research/               # Sources + coverage matrix
├── scripts/                # Research + validation scripts
└── tests/                  # Smoke tests
```

---

## Auth (Shared)

All skills use Application Default Credentials (ADC) unless the skill specifies otherwise.

```bash
# Developer
gcloud auth application-default login

# CI/CD (impersonate SA — no key file)
gcloud auth application-default login \
  --impersonate-service-account=SA@PROJECT.iam.gserviceaccount.com
```

See `shared/auth/` for full patterns.

---

## Coverage Matrix

See `research/coverage-matrix.md` for service-by-service skill status.

Target for v0.1: **zero `missing` entries for all first-wave services.**
