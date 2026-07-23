# GoogleCloud Plugin

> **Install once, and your coding agent gains a full Google Cloud delivery team — a vendor-objective solution designer, a GCP architect, an agentic-systems architect, plus security, SRE, and QA — wired into a design-first, security-first delivery gate.**

Skill libraries for Google Cloud are everywhere. What they miss is the operating contract: who designs before anyone codes, who signs off on least-privilege before anything deploys, what "done" means when an agent ships to a billable cloud. This plugin ships that contract, with the GCP know-how bolted in.

One install gives an agent (Claude, Codex, or Antigravity) five personas, eleven service skills, the MCP server map, and a research pipeline that keeps every reference current — because a plugin that silently goes stale is worse than no plugin at all.

The plugin is **GCP-only and opinionated by design**. It spans the estate a builder actually touches — from Firebase and Cloud Run to BigQuery and GKE, and up through the agent frameworks that now sit on top: ADK, and the MCP / A2A / AP2 protocol stack, deployed on the Gemini Enterprise Agent Platform. Refine it for your team; keep the contract coherent while you do.

> **Speed is easy. Safe speed is engineered.**

---

## The Solution → Delivery Workflow

Every piece of work flows through sequential gates. No gate opens until the one before it clears. Human intent enters at the top; a human authorises production at the bottom. The AI personas scale the execution in between — they never grant their own authority.

```mermaid
sequenceDiagram
    autonumber
    actor Req as Requirement (Human intent)
    participant Sol as solution-designer (Tier 1 · vendor-objective)
    participant Arch as gcp-architect + agent-architect (Tier 2)
    participant Sec as gcp-security
    participant Impl as Service Skills (Cloud Run · GKE · BigQuery · …)
    participant QA as gcp-qa (+ agent-eval)
    actor Ops as gcp-ops (Human SRE sign-off)

    rect rgb(238, 242, 255)
        note over Req,Sol: Solution Gate — is this even GCP? (skip if unambiguously GCP-only)
        Req->>Sol: 1. Submit intent / problem
        Sol-->>Arch: 2. Master HLD + vendor scope (hands GCP slice down)
    end

    rect rgb(237, 233, 254)
        note over Arch: GCP Design Gate — design before code
        Arch->>Arch: 3. GCP HLD/LLD + ADRs (agentic: topology, protocols, model, eval set)
    end

    rect rgb(252, 231, 243)
        note over Arch,Sec: Security Gate — reviews the design, not the diff
        Arch->>Sec: 4. Submit design
        Sec-->>Impl: 5. Least-privilege IAM, no secrets, WAF pillar — pass or BLOCK
    end

    rect rgb(240, 253, 244)
        note over Sec,Impl: Implementation — known-good GCP patterns, cost-warned
        Impl->>Impl: 6. Build on google-cloud patterns; warn before every billable action
    end

    rect rgb(254, 249, 231)
        note over Impl,QA: Quality Gate — receipts, not polish
        Impl->>QA: 7. Submit candidate
        QA-->>Ops: 8. make gate (validate + lint + test) + agent-eval — pass or BLOCK
    end

    rect rgb(224, 242, 254)
        note over QA,Ops: Operational Readiness Gate — no dark production
        Ops->>Ops: 9. SLO + alerting + runbook present?
        Ops-->>Req: 10. Authorise release & emit status
    end
```

### Gate ownership

| Gate | Owner | Blocks release when |
| :--- | :--- | :--- |
| **Solution** | `solution-designer` | Vendor choice unclear, or GCP scope not delimited (skips if GCP-only) |
| **GCP Design** | `gcp-architect` (+ `agent-architect` if agentic) | No GCP HLD, or HLD contradicts the solution design |
| **Security** | `gcp-security` | IAM over-permissive, secrets in code, GCP risks unaddressed |
| **Quality** | `gcp-qa` (+ `agent-architect` agent-eval) | `make gate` fails, acceptance criteria unmet, agent eval fails |
| **Operational Readiness** | `gcp-ops` | No SLO, alerting, or runbook for a production workload |

The rule underneath every gate: **infer intent, never infer permission.** An AI persona drafts, designs, and validates; a named human authorises anything consequential, billable, or irreversible.

---

## What you install

**Five personas** — the team:

| Persona | Tier | Owns |
| :--- | :--- | :--- |
| `solution-designer` | 1 · vendor-agnostic | The overarching solution; objective vendor selection across GCP / AWS / Azure |
| `gcp-architect` | 2 · GCP | GCP infrastructure design — HLD/LLD, ADRs, IAM and network topology |
| `agent-architect` | 2 · GCP agentic | Agentic systems on GEAP — ADK, Agent Runtime, MCP/A2A/AP2, and agent evaluation |
| `gcp-security` | 3 | Least-privilege IAM, secrets, Well-Architected security pillar |
| `gcp-ops` | 3 | SLOs, alerting, runbooks, operational readiness |
| `gcp-qa` | 3 | Validation, linting, smoke tests, the quality gate |

**Eight first-wave service skills:** Cloud Run · GKE · IAM · BigQuery · Cloud Storage · Vertex AI · Networking · Logging/Monitoring.

**Three cross-cutting skills:** `mcp-servers` (Google-managed + self-hosted MCP setup) · `well-architected` (the six-pillar framework) · `terraform-gcp` (CFT + provider patterns).

---

## Validation

The plugin validates itself. Every skill conforms to a machine-readable contract; every reference URL is checked live; every source carries a retrieval date and content hash for audit.

```bash
make gate       # the 3-minute gate: validate + lint + test
make validate   # SKILL.md frontmatter contract
make lint       # every reference URL resolves (HTTP 200)
make test       # skill smoke tests
make check      # freshness: content-hash drift vs live GCP docs
make crawl      # refresh the research corpus (weekly)
```

Freshness is a feature, not a chore: `make check` runs weekly and flags any GCP doc that has drifted since it was last captured, so the plugin never quietly rots.

---

## About the author

I'm **Jaroslav Pantsjoha (JP)** — a Google Developer Expert, and I build on Google Cloud for a living and for fun. Most weekends there's a hackathon build or an exploration on the go, and the same lesson keeps landing: the model is the easy part. The durable engineering is the harness around it — the skills, the rules, the MCP servers, the gates, the evals.

I built this plugin to make my own life easier, and then to share it. I already run my [`join-the-team`](https://github.com/jpantsjoha/ai-native-developer-experience) harness and a set of global skills across projects; what I wanted was the same consistency aimed squarely at Google Cloud. GCP patterns and approaches tend to stick around longer than the week's model release — which makes them worth encoding once, properly, so every build starts from the same design-first, security-first baseline instead of re-deriving it each time.

This is that baseline: one coherent, current, complete Google Cloud builder experience I can hand to my community and colleagues — from Firebase to the AP2 / A2A / ADK frameworks — and know we are all working from the same contract.

Part of the **#HarnessEngineering** work and the Google Cloud / GDE community.

**Connect:** [linkedin.com/in/johas](https://www.linkedin.com/in/johas) · [github.com/jpantsjoha](https://github.com/jpantsjoha)

---

## Licence

Open source under the [MIT License](LICENSE) — free for personal and commercial use, modification, and redistribution.
