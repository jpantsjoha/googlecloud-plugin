# ADR-007: Adopt Agent Plugins 1.0.0 as the Packaging Contract

**Status:** Accepted
**Date:** 2026-08-07
**Supersedes:** the frontmatter portion of [ADR-005](ADR-005-skill-contract.md)

## Context

Agent Plugins 1.0.0 is a vendor-neutral specification for packaging Agent Skills
and MCP servers, co-maintained by Amazon, Cursor, Google, Microsoft, OpenAI and
Vercel. It fixes the problem this plugin had been solving by brute force: we
shipped four harness manifests (`.claude-plugin/`, `.kimi-plugin/`,
`gemini-extension.json`, `.agents/`) because every client wanted a different
wrapper around the same skills.

Audited against the specification, the plugin had two independent fatal faults:

1. `plugin.json` omitted `$schema`. The manifest schema is closed
   (`additionalProperties: false`) and lists `$schema` as required, so §5.2
   makes the omission fatal — a conformant client rejects the plugin outright.
2. All 17 skills carried top-level frontmatter outside the closed Agent Skills
   field set (`version`, `triggers`, `required_scopes`, `mcp_servers`, and on
   personas `persona`, `tier`, `gate`, `owns_eval`). Agent Plugins §6.1 requires
   clients to **skip** every non-conforming skill.

Together: a conformant client would have loaded nothing.

## Decision

Conform to Agent Plugins 1.0.0 and the Agent Skills specification it references,
and enforce both in CI.

**Manifest.** `plugin.json` declares
`https://agent-plugins.org/schemas/1.0.0/plugin.schema.json`. Only the ten
permitted top-level fields appear. Client-specific data, if ever needed, goes
under `extensions` keyed by reverse-domain namespace.

**Skills.** Frontmatter is reduced to `{name, description, license, metadata}`.
The routing keywords that lived in `triggers` are folded into `description` —
which is what a conformant client actually routes on — and the plugin's own
contract moves under `metadata` as namespaced string values:

```yaml
---
name: cloud-run
description: "Deploy and manage containerized workloads on Cloud Run. … Use when the user mentions: deploy to cloud run, serverless container, …"
license: MIT
metadata:
  "googlecloud-plugin/version": "0.1"
  "googlecloud-plugin/triggers": "deploy to cloud run, serverless container, …"
  "googlecloud-plugin/required-scopes": "run.services.create, run.services.get, …"
  "googlecloud-plugin/mcp-servers": "google-cloud-run"
---
```

`metadata` is specified as a map from string keys to string values, so lists are
comma-joined rather than nested. Keys are namespaced because the spec recommends
names unique enough to avoid collisions with other clients.

**MCP.** A root `mcp.json` becomes the portable MCP manifest, with an explicit
`type` discriminator. Two consequences drove its shape:

- It declares the `gcloud` server only. `toolbox` needs a user-specific
  `tools.yaml` path, which no Agent Plugins placeholder can express, so it stays
  a documented opt-in in `skills/mcp-servers/`.
- It declares no `env`. Only `${PLUGIN_ROOT}` and `${PLUGIN_DATA}` expand;
  everything else is passed through **literally**. `CLOUDSDK_CORE_PROJECT:
  "${GCP_PROJECT_ID}"` would have set the project to that 18-character string.
  Clients may inherit the ambient environment, and `gcloud-mcp` already reads
  both the project and ADC from it.

**Harness manifests stay.** The specification closes the `plugin.json` field set
and fixes component locations; it says nothing about sibling directories, and v1
deliberately ships no install or distribution mechanism. So `.claude-plugin/`,
`.kimi-plugin/`, `gemini-extension.json` and `.agents/` remain, and existing
installs keep working. `mcp.json` is validated as a strict subset of `.mcp.json`
to stop the two drifting apart.

## Consequences

- ✅ A conformant client loads the plugin and all 17 skills. Previously: zero.
- ✅ Verified by tools we do not own — `skills-ref` (the reference validator) and
  `check-jsonschema` against both published schemas.
- ✅ `make spec` reports against the spec's own failure boundaries
  (FATAL / MCP / SKILL), so a violation's blast radius is visible.
- ✅ Portability stops being bespoke work per harness.
- ⚠️ Routing now depends entirely on `description` quality. Skills with adjacent
  scope need explicit "use X instead when…" clauses; a cross-harness routing
  test in Kimi surfaced four such pairs (iam↔gcp-security,
  gcp-ops↔logging-monitoring, vertex-ai↔agent-architect,
  gcp-architect↔solution-designer), now disambiguated in their descriptions.
- ⚠️ IAM scopes are no longer a YAML list. Tooling that reads
  `googlecloud-plugin/required-scopes` must split on `", "`.
- ⚠️ `mcp.json` and `.mcp.json` both exist and must not drift; `make manifest`
  enforces the subset relationship.
