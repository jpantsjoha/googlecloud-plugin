# ADR-006: Agent-Architect Persona (Agentic Architecture Specialist)

**Status:** Accepted  
**Date:** 2026-07-23

## Context

The plugin's ambition is authoritative Google Cloud coverage, and GCP's fastest-growing surface is agentic — the Gemini Enterprise Agent Platform (GEAP, formerly Vertex AI), ADK, Agent Runtime, and the MCP/A2A/AP2 protocol stack. This is a distinct design discipline:

- `solution-designer` decides vendor (GCP vs alternatives) — too high.
- `gcp-architect` designs GCP **infrastructure** (projects, IAM, networking, compute) — wrong layer.
- `vertex-ai` service skill covers platform *mechanics* (deploy an endpoint, call Gemini) — too narrow.

None of them own agentic **system** design: agent topologies, framework choice (ADK), grounding/RAG, memory, multi-agent orchestration, protocol layering, model selection, and — critically — agent **evaluation**, which is nothing like traditional software testing.

## Decision

Add `agent-architect` as a **Tier 2 domain specialist, sibling to `gcp-architect`**, plugging into the existing GCP Design Gate (no new gate). **GCP is always the target deployment platform** (Agent Runtime, Cloud Run, or GKE).

Boundary decisions (operator-selected):
- **Design + eval execution:** agent-architect owns agentic design AND *runs* agent evaluation itself — the one Tier 2 architect that executes its own gate, contributing an agent-eval criterion to the Quality Gate alongside `gcp-qa`'s software gate.
- **Full agentic stack scope:** topologies, ADK, Agent Runtime, MCP/A2A/AP2 protocols, grounding/RAG, memory, human-in-the-loop, model selection, evaluation.

Coherence rules:
- Complements the join-the-team `adk-expert` (pure ADK how-to) and aligns to `gcp-expert` as GEAP platform-currency authority — reference, don't contradict.
- Uses current GEAP naming in prose; preserves legacy `vertex-ai`/`agent_engine` literals in code, URLs, SDKs, and Terraform per the rebrand being branding-only.
- Enforces the Gemini model deprecation discipline — never pin preview IDs; reverify GA IDs in Model Garden for the GEAP surface.

## Consequences

- ✅ Closes a real gap: agentic system design + evaluation now has an owner
- ✅ Anchored on GCP deployment — not a generic agent skill
- ✅ Agent-eval becomes an explicit, owned release criterion (groundedness, trajectory, task success)
- ✅ Protocol stack (MCP/A2A/AP2) covered coherently with the `mcp-servers` skill
- ⚠️ Platform naming is fast-moving — mitigated by the freshness pipeline + external research (brief Task 7) + gcp-expert authority
- ⚠️ Overlaps `gcp-qa` on the eval gate by design — boundary stated explicitly (agent-eval here, software QA there) to avoid ambiguity
- ⚠️ Adds a 6th persona — accepted because the agentic discipline and its evaluation methodology are genuinely distinct, not a slice of an existing role
