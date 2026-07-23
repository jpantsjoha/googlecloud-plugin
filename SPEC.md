# GoogleCloud Plugin — Specification

**Status:** Draft v2 — Extended with persona model, gate system, engineering folder  
**Version:** 0.2 — Persona-first, gate-driven  
**Owner:** Development Team  
**Last updated:** 2026-07-23

---

## 1. Vision

A **single, authoritative Google Cloud plugin** that unifies every Google Cloud agent skill, MCP, blueprint, and know-how into one installable package. When a developer installs `googlecloud-plugin`, they immediately gain:

- All current Google Cloud services (Compute, Data, AI/ML, Networking, Security, Ops, etc.)
- All Google-managed + self-hosted MCP servers with setup guidance
- Best-practice blueprints, Terraform, samples, and examples from google-cloud org
- Automated freshness pipeline that discovers new GCP repos, skills, and samples weekly
- Safe-by-default quality gates (cost warnings, billable-action confirmations, dry-run modes)
- Full audit trail: every doc URL, retrieval date, content hash for compliance + source verification

**Target users:**
- Developers deploying applications on Google Cloud (any scale, any service)
- Platform engineers building landing zones or infrastructure-as-code on GCP
- AI agents (Claude, Codex, AGY) using the plugin to deliver Google Cloud work reliably

**Success metric:** First-wave services (Cloud Run, GKE, IAM, BigQuery, Cloud Storage, Vertex AI, Networking, Logging/Monitoring) are 100% covered and 0% stale. Plugin version 0.1 ships with zero missing skills.

---

## 2. Feature Spec

### What

- **Public repository** (`googlecloud-plugin/`): curated skills, validated MCPs, peer-reviewed blueprints, public release branches only
- **Working directory** (`_plugin/`): all research, planning, roadmaps, auditing, drafts (gitignored)
- **Skill structure**: mirrors `join-the-team` — each service gets a `skills/<service>/SKILL.md` + `references/` + optional `scripts/`
- **Research infrastructure**:
  - `research/SOURCES.md` — every doc URL + retrieval date + content hash (audit trail)
  - `research/coverage-matrix.md` — service → skill status (missing / drafted / normalized / validated)
  - `research/raw/<service>.md` — raw notes per service
- **Research scripts**:
  - `scripts/research_crawl.py` — fetches GCP docs, Google repo samples, blueprints; saves metadata + hashes
  - `scripts/validate_skills.py` — asserts every skill has valid SKILL.md + YAML frontmatter + refs
  - `scripts/check_links.py` — validates every URL in `references/` and `SOURCES.md` resolves (HTTP 200)
  - `scripts/freshness_check.py` — detects doc drift (hash mismatch) vs. live sources; reports stale docs
- **Orchestration**:
  - `PLUGIN.md` — top-level routing table; orchestrator instructions for AI agents
  - `plugin.yaml` — metadata, version, full skill index, MCP server listings
- **Shared modules**:
  - `shared/auth/` — ADC (Application Default Credentials), service-account patterns, credential discovery
  - `shared/discovery/` — how agents enumerate available skills at runtime
  - `shared/conventions.md` — skill structure contract + naming rules

### Why

1. **Consolidation:** Scatter of GCP skills/MCPs across projects → single source of truth
2. **Freshness:** GCP evolves weekly (new services, deprecations, examples); manual upkeep fails. Automated discovery + scheduled freshness checks guarantee plugin never silently goes stale
3. **Safety:** Billable actions (BigQuery queries, VM deployments) have cost warnings + confirmation gates. Destructive actions require dry-run first
4. **Auditability:** Every source doc carries URL + retrieval date; content hash tracks drift. Supports compliance + vendor audits
5. **Multi-agent support:** Claude, Codex, AGY all route through the same plugin contract

### Who

**Plugin consumers:**
- Developers using Claude Code / Claude API to build on Google Cloud
- Platform engineers designing GCP landing zones or IaC
- AI agents delegated to execute Google Cloud tasks

**Plugin maintainers (CI/CD + research):**
- Weekly freshness scanner (automated, posts PRs on drift detection)
- Human curator (reviews research, gates skill releases, approves coverage matrix updates)

### Constraints

1. **Data residency**: All research crawls must respect GCP API rate limits + robots.txt. Cache responses locally; no repeated fetches of identical URLs within 24 hours.
2. **Security**: No credentials hardcoded in skills or research scripts. Auth flows use ADC or explicit service-account paths. Skill contract includes required IAM scopes.
3. **Compliance**: Every reference doc must be attributable — URL + retrieval date is non-negotiable. Support vendor audits ("which GCP docs informed this skill?").
4. **Budget**: Research pipeline runs weekly, not on-demand (cost per crawl ~$0 API, ~1 min wall-clock). Freshness checks are read-only (no mutation, no cost).
5. **Scope — first wave**: Cloud Run, GKE, IAM, BigQuery, Cloud Storage, Vertex AI, Networking (VPC/Firewall/Cloud Load Balancer), Logging/Monitoring. Second wave (Dataflow, Pub/Sub, Cloud Functions, BigTable, Dataproc, etc.) comes after v0.1 validation.
6. **Quality bar**: Every skill must have ≥1 reference doc with live URL. Every URL must resolve. Every SKILL.md must parse YAML frontmatter without error.

### Acceptance Criteria

- [ ] Repo structure matches Phase 0 scaffold specification (all folders created, .gitignore excludes `_plugin/` and `.claude/local-CLAUDE.md`)
- [ ] `research/SOURCES.md` exists with ≥50 GCP docs enumerated (Cloud Run, GKE, IAM, BigQuery, Cloud Storage, Vertex AI, Networking, Logging/Monitoring, MCP servers, google-cloud org samples/blueprints)
- [ ] `research_crawl.py` runs and populates `research/raw/<service>.md` for all first-wave services
- [ ] `validate_skills.py` passes with 0 errors on existing skills (once Phase 1 drafts land)
- [ ] `check_links.py` validates ≥50 URLs from `research/SOURCES.md`, reports any 404s/timeouts
- [ ] `freshness_check.py` compares stored hashes vs. live sources, outputs a report
- [ ] `plugin.yaml` lists all first-wave skills with metadata (name, version, IAM scopes, triggers)
- [ ] `PLUGIN.md` routing logic resolves 5+ test prompts to the correct skill
- [ ] Main branch is protected (PRs required, reviews required before merge)
- [ ] `.claude/CLAUDE.md` (plugin construction guide) and `.claude/local-CLAUDE.md` (agent advisories) both exist and are gitignored
- [ ] Coverage matrix shows 0 `missing` for first-wave services before v0.1 tag
- [ ] Freshness pipeline triggers weekly via CI (e.g., GitHub Actions cron), posts auto-PR on drift

### Out of Scope (v0.1)

- Second-wave services (Dataflow, Pub/Sub, Cloud Functions, BigTable, Dataproc, etc.) — roadmapped for v0.2
- GCP Terraform modules beyond reference-and-link (hand-authored modules come later)
- GCP Cost Calculator integration (reference only in Phase 1 research)
- Multicloud (AWS, Azure) — googlecloud-plugin is GCP-only; aws-plugin and azure-plugin are separate repos
- Gemini-specific orchestration (out of scope for this plugin; handled at harness level)

---

## 3. High-Level Design

### Component Topology

```
developer installs googlecloud-plugin
         ↓
    [PLUGIN.md]
    (routing table)
         ↓
    skill discovery
         ↓
  ┌─────────────────────────────────┐
  │  skills/<service>/              │
  │  ├── SKILL.md (orchestrator)    │
  │  ├── references/                │
  │  │   ├── api-guide.md           │
  │  │   ├── cli-reference.md       │
  │  │   └── mcp-setup.md           │
  │  └── scripts/ (optional)        │
  │      └── deploy-helpers.sh      │
  └─────────────────────────────────┘
         ↓
  [shared/auth/] ← service account + ADC patterns
  [shared/discovery/] ← runtime enumeration
```

### Data Flow

1. **Research Phase (Phase 1)**:
   - `research_crawl.py` fetches GCP docs + google-cloud org repos
   - Stores in `research/raw/<service>.md` + metadata to `research/SOURCES.md`
   - Computes content hash for drift detection

2. **Skill Normalization (Phase 3)**:
   - For each service, author `SKILL.md` with routing + IAM scopes
   - Link to reference docs in `references/`
   - Populate `research/coverage-matrix.md` (status: drafted → validated)

3. **Orchestration (Phase 4)**:
   - `PLUGIN.md` + `plugin.yaml` route agent prompts to the correct skill
   - Agent loads skill, reads references, executes task
   - Shared auth module handles credential discovery

4. **Freshness (Automated)**:
   - Weekly: `freshness_check.py` runs, compares stored hashes vs. live sources
   - If drift detected: auto-PR with summary of changed docs
   - Human curator reviews, merges, or updates skill

### Integration Points

- **Harness**: googlecloud-plugin is installed as a `~/.claude/plugins/googlecloud-plugin/` plugin; agents discover via `/skill` registration
- **MCPs**: Google-managed + self-hosted MCP servers are listed in `plugin.yaml` with setup instructions under `skills/mcp-servers/references/`
- **Source repos**: google-cloud org (terraform-google, cloud-foundation-toolkit), official GCP samples, community blueprints
- **CI/CD**: GitHub Actions cron trigger weekly `freshness_check.py` + auto-PR on drift

### Failure Modes & Recovery

| Failure Mode | Detection | Recovery |
|---|---|---|
| GCP API rate-limit hit during research crawl | `research_crawl.py` returns HTTP 429 | Retry with exponential backoff; cache locally |
| Source doc URL returns 404 | `check_links.py` fails | Auto-PR flags URL as stale; curator updates reference |
| Skill SKILL.md has invalid YAML | `validate_skills.py` returns error | Pre-commit hook rejects; developer fixes frontmatter |
| Content hash mismatch (doc updated) | `freshness_check.py` reports drift | Auto-PR suggests refresh; curator decides: merge or skip |
| Agent skill not found in routing table | `PLUGIN.md` lookup fails | Graceful fallback: list available skills + suggest closest match |

---

## 4. Architecture Decisions (ADRs)

### ADR-001: Split Working / Public Directories

**Context:**  
Plugin construction involves research, planning, audits, and potentially stale/rejected drafts. Committing all of this to main pollutes the public repo and creates noise for users.

**Decision:**  
Use two directories:
- `_plugin/` (gitignored) — all planning, research output, roadmaps, auditing, drafts
- `googlecloud-plugin/` (public) — only curated, peer-reviewed, quality-gated skills and releases

**Consequences:**
- ✅ Public repo stays clean; users only see stable, validated content
- ✅ Builders have space to experiment without risk of broken releases
- ✅ Review gate (research → skill draft → review → public release) is enforced structurally
- ⚠️ Need clear gitignore to prevent accidental commits of `_plugin/` content

---

### ADR-002: Content Hash + URL Audit Trail

**Context:**  
GCP evolves rapidly. Skill references must remain current. Manual "check if docs changed" is unreliable; automated detection is required for compliance + vendor audits.

**Decision:**  
Every reference doc is stored with:
- Source URL
- Retrieval date (ISO 8601)
- Content hash (SHA256 of raw response body)
- Last-modified header (if present)

`freshness_check.py` runs weekly, re-fetches, and flags any hash mismatch.

**Consequences:**
- ✅ Drift is detected automatically; no silent staleness
- ✅ Audit trail supports compliance ("which docs informed this skill?")
- ✅ Curator has weekly report: which docs changed, by how much
- ⚠️ Adds ~1 sec per URL fetch; crawl time is ~5 min for 50 docs (acceptable for weekly schedule)
- ⚠️ Must handle redirects (301/302) gracefully; follow them but log the chain

---

### ADR-003: First-Wave Service Scope (v0.1)

**Context:**  
Google Cloud has 200+ services. Attempting to cover all is a project unto itself. v0.1 must ship with non-zero coverage and credibility.

**Decision:**  
v0.1 targets **7 first-wave services**:
1. Cloud Run
2. GKE
3. IAM
4. BigQuery
5. Cloud Storage
6. Vertex AI
7. Networking (VPC, Firewall, Cloud Load Balancer, Cloud Armor)
8. Logging/Monitoring (Cloud Logging, Cloud Trace, Cloud Profiler)

Each gets a validated skill. MCP servers (Google-managed) are a separate skill. Second wave (Dataflow, Pub/Sub, Cloud Functions, etc.) follows after v0.1 validation.

**Consequences:**
- ✅ Achievable in reasonable time (2-3 weeks of research + normalization)
- ✅ Covers the "critical path" services (most GCP workloads use ≥3 of these)
- ✅ Sets quality bar: zero missing, zero stale for v0.1
- ⚠️ Users with second-wave needs must wait for v0.2
- ⚠️ Roadmap must be transparent about scope

---

### ADR-004: Safe-by-Default Billable Actions

**Context:**  
BigQuery queries, VM deployments, and CI/CD runs incur cost. Accidental execution can be expensive.

**Decision:**  
Every billable skill includes:
1. Cost estimate (if available) before execution
2. Explicit confirmation gate ("Continue? [y/N]")
3. Optional dry-run mode (e.g., `bq query --dry_run` for BigQuery)
4. Audit log entry (who, what, when, estimated cost)

**Consequences:**
- ✅ Prevents accidental cost spikes
- ✅ Audit trail for billing accountability
- ✅ Developers can prototype safely with dry-run
- ⚠️ Slightly slower interaction (one confirmation per billable action)
- ⚠️ Cost estimate accuracy depends on GCP pricing API availability

---

### ADR-005: Skill Contract = SKILL.md Frontmatter

**Context:**  
Agents need to discover and route to skills at runtime. A standard contract ensures consistency.

**Decision:**  
Every skill has a `SKILL.md` with YAML frontmatter:
```yaml
---
name: cloud-run
description: "Deploy and manage containerized workloads on Cloud Run"
version: 0.1
triggers: ["deploy to cloud run", "create cloud run service", "scale cloud run"]
required_scopes:
  - run.services.create
  - run.services.delete
  - run.services.get
  - run.services.list
  - run.services.update
mcp_servers: []
---
```

Followed by H1 title + comprehensive routing + references.

**Consequences:**
- ✅ Machine-readable skill metadata for discovery
- ✅ Agents know required IAM scopes before attempting task
- ✅ Consistent structure across all skills
- ⚠️ Must validate frontmatter format (tool: `validate_skills.py`)
- ⚠️ Requires skill authors to understand IAM scope mapping

---

## 5. Constraints & Non-Negotiables

### Security

- **No hardcoded credentials** in any skill or script. Use ADC (Application Default Credentials) or explicit service-account file paths only.
- **Secrets in references must be redacted** — if a sample shows a key, redact or use placeholder.
- **IAM scopes are explicit** — every skill lists required scopes in frontmatter; agents can enforce least-privilege policy.

### Compliance & Auditability

- **Every reference doc must have a source URL + retrieval date.** Non-negotiable. Supports vendor audits ("which docs did you use?").
- **Content hashes detect drift.** If a doc changes, `freshness_check.py` flags it within 24 hours.
- **Research sources are archived locally** — `research/raw/<service>.md` is the snapshot of what was retrieved; live URLs may change.

### Performance & Scale

- **Research crawl:** ~5 min for 50 docs (acceptable for weekly schedule).
- **Freshness check:** ~30 sec for 50 URLs (read-only; no cost).
- **Skill discovery at runtime:** <1 sec to route prompt to correct skill.
- **Rate limits:** Respect GCP API + GitHub API rate limits; add delays as needed.

### Quality Bar

- **Zero invalid SKILL.md files.** `validate_skills.py` rejects any skill with malformed frontmatter.
- **Zero broken URLs.** `check_links.py` reports all 404s; curator updates or removes references.
- **Zero stale docs (first-wave).** Before v0.1 release, coverage matrix must show all first-wave services ≥ "validated".

### Team Capability

- **One curator** can manage the plugin (weekly freshness check, reviews, releases).
- **Builders** (Claude agents, humans) author skills following the SKILL.md contract.
- **CI/CD** (GitHub Actions) runs research crawl + freshness check on schedule.

---

## 6. Acceptance Criteria (Testable)

### Phase 0 — Scaffold (Definition of Done)

- [ ] Repo structure created (all folders listed in spec)
- [ ] `.gitignore` excludes `_plugin/`, `.claude/local-CLAUDE.md`, `research/raw/`, research cache
- [ ] Main branch protection enabled (PRs required, reviews required)
- [ ] Initial commit: "chore: bootstrap googlecloud-plugin structure"

### Phase 1 — Research (Definition of Done)

- [ ] `research/SOURCES.md` enumerated with ≥50 GCP docs (Cloud Run, GKE, IAM, BigQuery, Cloud Storage, Vertex AI, Networking, Logging/Monitoring, MCP servers, google-cloud org samples)
- [ ] `research_crawl.py` runs end-to-end with 0 uncaught exceptions (test: `python scripts/research_crawl.py --help && python scripts/research_crawl.py 2>&1 | tail -5`)
- [ ] `research/raw/<service>.md` created for all 8 first-wave services with raw notes + metadata
- [ ] `research/coverage-matrix.md` initialized with 8 rows (one per service), status = "researched"

### Phase 2 — Research Scripts (Definition of Done)

- [ ] `validate_skills.py` returns 0 errors on any valid SKILL.md; reports specific YAML line on error
- [ ] `check_links.py` validates 50+ URLs, reports HTTP status + response time per URL
- [ ] `freshness_check.py` compares stored hashes vs. live sources, outputs diff + recommendations
- [ ] All scripts have `--help` and exit with code 0 (success) or 1 (error)
- [ ] Scripts run in isolation (no shared state; safe to run sequentially or in parallel)

### Phase 3 — Normalize Skills (Definition of Done)

- [ ] 8 skills created: `skills/cloud-run/SKILL.md`, `skills/gke/SKILL.md`, ... (one per first-wave service)
- [ ] Each SKILL.md has valid YAML frontmatter + ≥1 reference URL with live link
- [ ] `scripts/validate_skills.py` passes on all 8 skills with 0 errors
- [ ] `scripts/check_links.py` validates all reference URLs (all return HTTP 200)
- [ ] Coverage matrix updated: status = "normalized" for all 8 services

### Phase 4 — Orchestration (Definition of Done)

- [ ] `PLUGIN.md` exists with routing table + top-level orchestrator instructions
- [ ] `plugin.yaml` lists all 8 first-wave skills + MCP server listings + version
- [ ] Routing logic resolves 5+ test prompts to correct skill (e.g., "deploy to cloud run" → cloud-run skill)
- [ ] `shared/auth/README.md` documents ADC + service-account patterns
- [ ] `shared/discovery/README.md` documents how agents enumerate skills

### Phase 5 — QA Gate (v0.1 Release Readiness)

- [ ] `validate_skills.py`, `check_links.py`, `freshness_check.py` all pass with 0 errors
- [ ] Coverage matrix: all 8 first-wave services status = "validated"
- [ ] `plugin.yaml` indexes all 8 skills + version bumped to 0.1.0
- [ ] Smoke tests pass: each skill's routing can be invoked without error
- [ ] CI/CD: freshness pipeline configured to run weekly; test run successful
- [ ] `.claude/CLAUDE.md` (plugin construction) + `.claude/local-CLAUDE.md` (agent advisories) both written + gitignored
- [ ] Main branch release tag created: `v0.1.0`

---

## 7. Rollback & Contingency

### If Research Crawl Fails

- Retry with exponential backoff (max 3 times, 30-sec intervals)
- If persistent: manually add source to `research/SOURCES.md`; flag in weekly report
- Plugin can ship without that particular source; use alternative doc

### If Skill Validation Fails

- Skill does not appear in `plugin.yaml` until it passes validation
- Pre-commit hook rejects invalid SKILL.md files (prevents merge)
- Curator must fix frontmatter before release

### If Reference URL Returns 404

- `check_links.py` flags it; auto-PR suggests removal or replacement
- Curator updates reference or marks as deprecated
- Skill can ship without that reference if ≥1 valid reference remains

### If Freshness Check Detects Drift

- Auto-PR posted with summary (which docs changed)
- Curator reviews diff; decides: merge (refresh skill) or close (no change needed)
- Plugin remains at current version until curator acts

---

## 8. Success Metrics (v0.1)

| Metric | Target | Rationale |
|--------|--------|-----------|
| First-wave coverage | 8/8 services (100%) | Credibility: ship complete in v0.1, not partial |
| Reference staleness | 0/50 URLs stale | Freshness: no silent decay |
| SKILL.md validation | 100% pass rate | Quality: all skills conform to contract |
| Research pipeline runtime | <10 min | Operational: weekly crawl completes in 1 CI slot |
| Freshness pipeline runtime | <2 min | Operational: weekly check is fast feedback |
| Mean time to detect drift | <24 hours | Reliability: discovered within 1 day of GCP change |

---

## 9. Cost & Resource Estimate

### Development Effort

| Phase | Effort | Owner |
|-------|--------|-------|
| Phase 0 (Scaffold) | 30 min | Agent |
| Phase 1 (Research) | 4 hours | Agent (crawl + manual review) |
| Phase 2 (Scripts) | 3 hours | Agent (validate, check_links, freshness) |
| Phase 3 (Skills) | 8 hours | Agent + human curator (normalize + review) |
| Phase 4 (Orchestration) | 2 hours | Agent |
| Phase 5 (QA) | 2 hours | Agent + curator (smoke test + release) |
| **Total** | **~19-20 hours** | |

### Operational Cost (Ongoing)

- **Research crawl (weekly):** ~$0 API cost (GCP docs are public + robots.txt compliant)
- **Freshness check (weekly):** ~$0 (read-only HTTP requests)
- **Curator overhead:** ~30 min/week (review auto-PR, merge or close)
- **GitHub Actions:** ~2 min/run × 52 runs/year = ~104 min/year (negligible cost)

---

## 10. Validation Checklist (for you)

Before proceeding to Phase 0 scaffold, confirm:

- [ ] Vision is clear: "all GCP skills + MCPs + know-how, 1 installable plugin"
- [ ] First-wave scope (8 services) is achievable and credible
- [ ] Research pipeline (crawl + freshness scripts) is the right automation approach
- [ ] Split working/public directories (ADR-001) matches your intent
- [ ] Safe-by-default for billable actions is a hard requirement
- [ ] Acceptance criteria are testable + measurable
- [ ] v0.1 success metric (8/8 services, 0 stale URLs) is what you want
- [ ] Effort estimate (~20 hours total) is realistic
- [ ] Ready to commit to weekly freshness maintenance post-launch

If you have feedback on any of these, let me know before I proceed to Phase 0.

---

---

## 11. Persona Model — The GCP Team (Added v0.2)

The plugin is **not just a skill library** — it installs an operational GCP team. Four core personas are available from day one. Every service skill references these personas as the authority layer above it.

### Core Personas

Two tiers of design authority, then delivery + assurance.

**Tier 1 — Solution Authority (vendor-agnostic)**

| Persona | Skill | Role | Gate Responsibility |
|---------|-------|------|---------------------|
| **Solution Designer** | `skills/solution-designer/` | Vendor-agnostic. Sits above all cloud-specific personas. Owns the overarching solution design — may span GCP, AWS, Azure, on-prem, or SaaS. Not GCP-biased: researches, proves, and validates that the proposed solution works across all vendors mentioned. Produces the master HLD that scopes each cloud domain's work. Hands GCP scope to gcp-architect; hands AWS scope to an AWS architect (or equivalent). Objective: if another cloud is genuinely better for a component, says so. | **Solution Gate** — no domain architect begins work without a solution-designer HLD that defines their slice |

**Tier 2 — Domain Architecture (cloud-specific)**

| Persona | Skill | Role | Gate Responsibility |
|---------|-------|------|---------------------|
| **GCP Architect** | `skills/gcp-architect/` | 100% Google Cloud focused. Receives the GCP-scoped portion of the solution-designer HLD. Design-first within GCP. Generates GCP-specific HLD/LLD, authors GCP ADRs. Aware of all GCP repos, examples, patterns, policies, principles, and MCPs. Does not make vendor-selection decisions — those belong to solution-designer. | **GCP Design Gate** — blocks GCP implementation without a current GCP HLD aligned to the solution design |
| **Agent Architect** | `skills/agent-architect/` | Agentic-systems specialist, sibling to gcp-architect. Owns agentic application design on the Gemini Enterprise Agent Platform (GEAP) — topologies, ADK, Agent Runtime, MCP/A2A/AP2 protocol stack, grounding/RAG, memory, HITL, model selection. GCP is always the deployment target. Uniquely also **runs agent evaluation** (design + execution). See ADR-006. | **GCP Design Gate** (agentic specialist) + **agent-eval** contribution to the Quality Gate |

**Tier 3 — Delivery + Assurance (cross-cutting)**

| Persona | Skill | Role | Gate Responsibility |
|---------|-------|------|---------------------|
| **Security** | `skills/gcp-security/` | Enforces GCP Well-Architected Framework security pillar. Least-privilege IAM. Secrets management. No hardcoded credentials. Controls review before any implementation. Flags OWASP + GCP-specific risks. Also reviews solution-designer output for cross-cloud security gaps. | **Security Gate** — reviews design before implementation starts |
| **Operations / SRE** | `skills/gcp-ops/` | Monitors, observes, logs, reports. Defines SLOs. Owns alerting policy, runbooks, incident response. Knows what healthy looks like in production for each GCP service. | **Operational Readiness Gate** — validates observability exists before release |
| **QA / Review** | `skills/gcp-qa/` | Critiques and evaluates designs, implementations, and release candidates. Validates against acceptance criteria. Linting, link checks, freshness, smoke tests. Raises blockers. Owns the quality contract for both the plugin itself and solutions built with it. | **Quality Gate** — validates implementation before any release tag |

### Persona Routing

Each persona skill follows the same SKILL.md contract but has an elevated role:

```yaml
# Example: gcp-architect frontmatter
---
name: gcp-architect
description: "Design-first GCP architect. Generates HLD/LLD, owns ADRs, enforces design gate. Aware of all GCP repos, patterns, MCPs, and Well-Architected Framework."
version: 0.1
persona: true
triggers:
  - "design a solution"
  - "architect this"
  - "how should we build"
  - "what's the approach for"
  - "HLD for"
  - "ADR for"
gate: design
required_scopes: []
mcp_servers: []
references:
  - url: https://cloud.google.com/architecture
    title: Google Cloud Architecture Framework
    retrieved: 2026-07-23
---
```

### Gate System (Design-First Enforcement)

Gates are sequential and blocking. No phase begins until the previous gate clears.

```
User request / Feature
        ↓
[SOLUTION GATE] ── solution-designer ───────────────────────────────────────────
        │  • Is this multi-vendor or does it need vendor-objective validation?
        │  • Master HLD produced / updated with vendor scope breakdown?
        │  • GCP scope explicitly defined and handed to gcp-architect?
        │  • Cross-vendor integration points documented?
        │  BLOCK if: vendor selection unclear, or GCP scope not delimited
        │  SKIP if: unambiguously GCP-only with no cross-cloud components
        ↓
[GCP DESIGN GATE] ── gcp-architect ─────────────────────────────────────────────
        │  • GCP HLD exists or is updated (aligned to solution-designer HLD)?
        │  • LLD exists for complex GCP components?
        │  • GCP ADR raised for significant decisions?
        │  • All GCP integration points, patterns, and MCPs identified?
        │  BLOCK if: no GCP HLD, or HLD contradicts solution design
        ↓
[SECURITY GATE] ── gcp-security ────────────────────────────────────────────────
        │  • IAM scopes are least-privilege?
        │  • No secrets in code or config?
        │  • Well-Architected security pillar reviewed?
        │  • GCP-specific risks addressed (public buckets, default SAs, etc.)?
        │  • Cross-cloud security boundaries reviewed (if multi-vendor)?
        │  BLOCK if: known security gap or IAM over-permissioning
        ↓
[IMPLEMENTATION] ── service skills (Cloud Run, GKE, BigQuery, etc.) ────────────
        │  • Uses GCP examples and known-good patterns from google-cloud org
        │  • References Well-Architected Framework where applicable
        │  • Warns before billable actions (cost estimate + confirmation gate)
        ↓
[QUALITY GATE] ── gcp-qa ───────────────────────────────────────────────────────
        │  • Validates against acceptance criteria
        │  • Linting + link checks + freshness checks pass
        │  • Smoke tests pass
        │  BLOCK if: acceptance criteria unmet or tests fail
        ↓
[OPERATIONAL READINESS GATE] ── gcp-ops ─────────────────────────────────────────
        │  • Alerting policy defined?
        │  • Runbook exists?
        │  • SLOs documented?
        │  • Dashboards configured?
        │  BLOCK if: no observability for a production workload
        ↓
Release / Delivery
```

---

## 12. Engineering + Architecture Folder Structure (Added v0.2)

### Revised Repository Layout

```
googlecloud-plugin/
├── PLUGIN.md                     # Top-level orchestrator + routing table
├── plugin.yaml                   # Metadata, version, skill index, MCP listings
│
├── skills/
│   │
│   ├── # ─── TIER 1: SOLUTION AUTHORITY (vendor-agnostic) ──────────────────
│   ├── solution-designer/        # Overarching solution design — vendor-objective
│   │   ├── SKILL.md              # Solution gate, multi-vendor HLD, vendor scope breakdown
│   │   └── references/           # Cloud comparison frameworks, multi-cloud patterns, WAF refs
│   │
│   ├── # ─── TIER 2: DOMAIN ARCHITECTURE (GCP-specific) ─────────────────────
│   ├── gcp-architect/            # 100% GCP-focused architect persona
│   │   ├── SKILL.md              # GCP design gate, HLD/LLD, ADR authoring, GCP patterns
│   │   └── references/           # GCP Architecture Framework, CFT, google-cloud org repos
│   │
│   ├── # ─── TIER 3: DELIVERY + ASSURANCE (cross-cutting) ───────────────────
│   ├── gcp-security/             # Security enforcer persona
│   │   ├── SKILL.md              # Well-Architected security, IAM, secrets controls
│   │   └── references/           # GCP security best practices, WAF security pillar
│   ├── gcp-ops/                  # Operations/SRE persona
│   │   ├── SKILL.md              # SLOs, alerting, runbooks, incident response
│   │   └── references/           # Cloud Logging/Monitoring, SRE book, GCP ops patterns
│   ├── gcp-qa/                   # QA/Review persona
│   │   ├── SKILL.md              # Critique, validate, lint, freshness, acceptance testing
│   │   └── references/           # Testing patterns, smoke test contracts
│   │
│   ├── # ─── SERVICE SKILLS (first wave v0.1) ──────────────────────────────
│   ├── cloud-run/
│   ├── gke/
│   ├── iam/
│   ├── bigquery/
│   ├── cloud-storage/
│   ├── vertex-ai/
│   ├── networking/               # VPC, Firewall, Cloud Load Balancer, Cloud Armor
│   ├── logging-monitoring/       # Cloud Logging, Cloud Trace, Cloud Profiler
│   │
│   ├── # ─── CROSS-CUTTING SKILLS ────────────────────────────────────────
│   ├── mcp-servers/              # All Google-managed + self-hosted MCP servers
│   ├── well-architected/         # GCP Well-Architected Framework reference skill
│   ├── terraform-gcp/            # Terraform patterns for GCP (CFT, google-cloud org)
│   └── firebase/                 # Firebase (v0.2 candidate, stub in v0.1)
│
├── architecture/
│   ├── HLD/                      # High-level designs — one doc per feature/use case
│   │   └── README.md             # HLD template + when to create vs update
│   ├── LLD/                      # Low-level designs — detail from HLD
│   │   └── README.md             # LLD template
│   ├── decisions/                # ADRs — numbered sequentially (ADR-001, ADR-002, ...)
│   │   ├── ADR-001-split-working-public.md
│   │   ├── ADR-002-content-hash-audit.md
│   │   ├── ADR-003-first-wave-scope.md
│   │   ├── ADR-004-safe-by-default-billable.md
│   │   └── ADR-005-skill-contract.md
│   └── patterns/                 # Reusable GCP patterns extracted from google-cloud org
│       └── README.md
│
├── engineering/
│   ├── features/                 # Feature implementation docs (lightweight, per-feature)
│   │   └── README.md             # Feature doc template
│   ├── use-cases/                # Full business use case definitions (when scope is broader)
│   │   └── README.md             # Use case template
│   └── runbooks/                 # Operational runbooks (feeding gcp-ops)
│       └── README.md
│
├── shared/
│   ├── auth/                     # ADC + service-account patterns
│   ├── discovery/                # Agent skill enumeration at runtime
│   └── conventions.md            # Skill structure contract + naming rules
│
├── research/
│   ├── SOURCES.md                # URL + retrieval date + hash (audit trail)
│   ├── coverage-matrix.md        # Service → skill status
│   └── raw/                      # Raw notes per service (gitignored for publication)
│
├── scripts/
│   ├── research_crawl.py         # Fetch + cache GCP docs + google-cloud org repos
│   ├── validate_skills.py        # SKILL.md frontmatter contract validation
│   ├── check_links.py            # Verify all reference URLs resolve
│   └── freshness_check.py        # Detect stale docs vs. live sources
│
├── tests/
│   └── skill-smoke-tests/        # Per-skill smoke tests (routing + frontmatter)
│
├── .claude/
│   ├── CLAUDE.md                 # Plugin construction guide (gitignored)
│   └── local-CLAUDE.md           # Agent advisories for this session (gitignored)
│
└── _plugin/                      # GITIGNORED — all planning, research, roadmaps, drafts
    ├── planning/                  # Roadmap, objectives, OKRs
    ├── research/                  # Raw research output (pre-curation)
    ├── audits/                    # Quality audit reports
    └── staging/                   # Draft skills awaiting review/release
```

### When to Create HLD vs Feature Doc vs Use Case

| Artefact | When | Location | Owned by |
|----------|------|----------|----------|
| **HLD** | Any feature/change touching ≥2 components OR any new service integration OR any infrastructure change | `architecture/HLD/<name>.md` | gcp-architect persona |
| **LLD** | When HLD reveals implementation complexity or ambiguity in a specific component | `architecture/LLD/<name>.md` | gcp-architect persona |
| **ADR** | Any significant technical decision (framework choice, auth pattern, data model, security boundary) | `architecture/decisions/ADR-NNN-<title>.md` | gcp-architect persona |
| **Feature doc** | Single-service feature or enhancement (1 component, low complexity) | `engineering/features/<name>.md` | Implementation owner |
| **Use case doc** | Multi-service business use case (e.g. "deploy ML pipeline end-to-end") | `engineering/use-cases/<name>.md` | gcp-architect + implementation owner |
| **Runbook** | Operational procedure (deployment, incident response, rollback) | `engineering/runbooks/<name>.md` | gcp-ops persona |

---

## 13. Ways of Working — Coherence with join-the-team (Added v0.2)

This plugin installs alongside the join-the-team harness. They must not conflict. Coherence rules:

### How they interlock

| join-the-team skill | googlecloud-plugin equivalent | Relationship |
|--------------------|-------------------------------|--------------|
| `the-architect` | `gcp-architect` | gcp-architect is the GCP-specific instance; the-architect is the harness-level authority. For GCP work, gcp-architect leads and routes to the-architect for cross-system decisions |
| `adversarial-gate` | `gcp-qa` | gcp-qa handles GCP-specific critique; adversarial-gate handles strategic/high-stakes decisions. Both can run on the same output |
| `pr-reviewer` | Inherited from harness | Plugin PRs use the harness pr-reviewer; no duplicate reviewer needed |
| `spec-first-delivery` | gcp-architect's design gate | gcp-architect enforces spec-first for GCP work; spec-first-delivery is the harness-level escalation |
| `release-readiness` | gcp-ops + gcp-qa gates | Plugin uses these two for release; harness release-readiness is the final authority |
| `domain-validator` | gcp-security | gcp-security handles GCP domain validation; domain-validator is the harness escalation |

### Golden rule

**The join-the-team harness sets risk tiers and authority. The googlecloud-plugin personas own GCP domain knowledge and GCP-specific gates. The harness always wins on authority; the plugin always wins on GCP specifics.**

### Plugin Ways of Working (in addition to harness rules)

1. **Design gate is non-negotiable.** No GCP implementation begins without gcp-architect producing or updating an HLD. This is an unconditional pre-condition.
2. **Security reviews happen at design time, not after.** gcp-security reviews the design (HLD/LLD), not the code diff. Security is an input to engineering, not a check on the output.
3. **All GCP examples and patterns must be attributable.** If a skill references a GCP sample, blueprint, or Terraform module, the source URL + retrieval date must be in `research/SOURCES.md`.
4. **Billable actions always confirm.** Any action that incurs GCP cost warns the user with a cost estimate before execution. No silent spend.
5. **Secrets never appear in skills, references, or research.** Credentials discovered during research are noted by location only — values are never recorded.
6. **Main branch is release-only.** Research, drafts, and planning live in `_plugin/` (gitignored). Skills only merge to main after passing gcp-qa validation.

---

## 14. MCP Tooling — First-Class Deliverable (Added v0.2)

When a developer installs `googlecloud-plugin`, they get not just skills but **fully configured and maintained MCP server access**. MCP tooling is a first-class deliverable alongside the skills, not an afterthought.

### MCP Coverage Strategy

Every MCP entry has:
- **Setup instructions** (install, auth, env vars required)
- **Maintenance status** (version, last-verified date, deprecation flags)
- **Capability map** (which GCP operations it enables)
- **Freshness hook** (included in `freshness_check.py` to detect version updates)
- **Fallback** (what to do if the MCP server is unavailable — gcloud CLI equivalent)

### Google-Managed MCP Servers (Priority 1)

These are Google's own hosted MCP servers — single API, no self-hosting required.

| MCP Server | Capability | Auth | Status Target |
|-----------|-----------|------|--------------|
| `google-cloud-run` | Deploy/manage Cloud Run services | ADC or SA key | v0.1 |
| `google-bigquery` | Query/manage BigQuery datasets | ADC | v0.1 |
| `google-gke` | GKE cluster management | ADC + kubeconfig | v0.1 |
| `google-storage` | Cloud Storage bucket ops | ADC | v0.1 |
| `google-vertex-ai` | Vertex AI model/endpoint management | ADC | v0.1 |
| `google-iam` | IAM policy management | ADC | v0.1 |
| `google-logging` | Cloud Logging query/ingest | ADC | v0.1 |
| `google-monitoring` | Metrics, alerting policy management | ADC | v0.1 |
| `firebase` | Firebase project management | ADC | v0.2 |
| `google-pubsub` | Pub/Sub topic/subscription management | ADC | v0.2 |

### Self-Hosted / Community MCP Servers (Priority 2)

Where Google-managed MCPs don't exist, the plugin covers self-hosted or community alternatives.

| MCP Server | Capability | Notes |
|-----------|-----------|-------|
| `gcloud-mcp` | Wraps `gcloud` CLI for broad GCP coverage | Community — requires local gcloud |
| `terraform-gcp-mcp` | Terraform plan/apply for GCP resources | Community — requires Terraform + credentials |
| `k8s-mcp` | Kubernetes API for GKE clusters | Standard k8s MCP; works with GKE kubeconfig |
| `google-workspace-mcp` | Google Workspace (Drive, Calendar, Gmail) | Google-managed |

### MCP Skill Structure

Each MCP server gets an entry in `skills/mcp-servers/` with:

```
skills/mcp-servers/
├── SKILL.md                          # Routing + overview of all MCP servers
├── references/
│   ├── google-managed-mcps.md        # All Google-managed servers: setup + auth
│   ├── self-hosted-mcps.md           # Community/self-hosted: install + configure
│   └── mcp-troubleshooting.md        # Common auth failures + fallback patterns
└── scripts/
    ├── verify_mcp_connections.py     # Test each configured MCP server is reachable
    └── mcp_setup_wizard.sh           # Interactive setup: walks user through install + auth
```

### MCP Maintenance

MCP servers are explicitly included in the **freshness pipeline**:

- `research_crawl.py` checks each MCP server's GitHub repo for new releases
- `freshness_check.py` compares pinned version vs. latest release tag
- If a new version is available: auto-PR flagging update + release notes summary
- `verify_mcp_connections.py` runs in CI weekly to confirm all configured MCPs respond

### MCP Auth Architecture

All MCP servers authenticate via the shared auth module (`shared/auth/`):

```
shared/auth/
├── adc.md            # Application Default Credentials — how agents use it
├── service-account.md # SA key file pattern — when and how to use
├── gcloud-login.md   # gcloud auth login / application-default login flow
└── mcp-auth.md       # How each MCP server consumes ADC or SA credentials
```

**Rule:** No MCP server configuration ever stores a credential value. Auth is always via:
1. ADC (preferred, `gcloud auth application-default login`)
2. SA key file path (referenced by path, never content)
3. Workload Identity (for GKE/Cloud Run running agents)

---

## Next Steps

Once you validate this spec:

1. **Phase 0 — Scaffold** (30 min): Create folder structure, .gitignore, protect main branch
2. **Phase 1 — Research** (4 hours): Crawl GCP docs + google-cloud org; populate `research/raw/` + `SOURCES.md`
3. **Phase 2 — Scripts** (3 hours): Write validate/check_links/freshness tools
4. **Phase 3 — Skills** (8 hours): Normalize 8 first-wave skills + references
5. **Phase 4 — Orchestration** (2 hours): Write PLUGIN.md + plugin.yaml + shared auth/discovery
6. **Phase 5 — QA** (2 hours): Smoke tests + CI/CD + release v0.1.0

**Ready to proceed?**
