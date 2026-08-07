# ADR-007: Adopt Agent Plugins 1.0.0 as the Packaging Contract

**Status:** Accepted
**Date:** 2026-08-07
**Supersedes:** the frontmatter portion of [ADR-005](ADR-005-skill-contract.md)

## Context

Agent Plugins 1.0.0 is an open, vendor-neutral specification for packaging Agent
Skills and MCP servers into portable plugins. Amazon, Cursor, Google, Microsoft,
OpenAI and Vercel are Core Maintainers. It removes the reason this repo carries
four near-duplicate manifests: the components were already portable, but the
wrapper around them was not.

An audit against the specification found two independent **fatal** faults.

**1. `plugin.json` omitted `$schema`.** The manifest schema is closed
(`additionalProperties: false`) and lists `$schema` in `required`. Specification
§5.2 makes a schema violation fatal — the client rejects the plugin entirely.

**2. Every skill was non-conformant.** The Agent Skills frontmatter field set is
closed: `name`, `description`, `license`, `compatibility`, `metadata`,
`allowed-tools`. ADR-005 mandated `version`, `triggers`, `required_scopes` and
`mcp_servers` as top-level fields, and personas added `persona`, `tier`, `gate`
and `owns_eval`. Agent Plugins §6.1 requires a client to **skip** each skill that
does not conform to the Agent Skills specification.

Together these meant a conformant client would load **nothing** — the plugin
would be rejected outright, and had it not been, all 17 skills would have been
silently skipped. The repo's own `make gate` passed throughout, because it
enforced ADR-005 rather than the published specs.

## Decision

Conform to Agent Plugins 1.0.0 and the Agent Skills specification it references.
Treat the published schemas, not this repo's conventions, as the authority.

**Manifest.** `plugin.json` declares
`https://agent-plugins.org/schemas/1.0.0/plugin.schema.json`. Its field set was
already within §5.2's permitted ten, so nothing else moved.

**MCP.** A new root `mcp.json` is the portable MCP manifest, with an explicit
`"type": "stdio"` transport discriminator — the schema's `oneOf` discriminates
on that field, so a server omitting it is skipped.

It declares the `gcloud` server **only**, and omits `env` entirely. Two reasons:

- Only `${PLUGIN_ROOT}` and `${PLUGIN_DATA}` expand. `${GCP_PROJECT_ID}` would
  have been passed through *literally*, setting `CLOUDSDK_CORE_PROJECT` to the
  17-character string `${GCP_PROJECT_ID}`. Clients MAY inherit the ambient
  environment, and `gcloud-mcp` already reads project and ADC from it.
- `toolbox` needs `--config <user-specific tools.yaml>`, which no spec
  placeholder can express. It remains a documented opt-in rather than a server
  that fails on every first install.

`mcp.json` is therefore deliberately a **subset** of the harness manifests.
`validate_plugin.py` enforces that relationship so the two cannot drift.

**Skills.** Frontmatter reduces to `name`, `description`, `license`, `metadata`.
The routing keywords from `triggers` fold into `description` — which is what a
conformant client actually routes on, and the specification asks descriptions to
carry the discriminating keywords. The plugin's own contract moves under
`metadata` as namespaced string values:

```yaml
---
name: cloud-run
description: "Deploy and manage containerized workloads on Cloud Run. … Use when
  the user mentions: deploy to cloud run, serverless container, gcloud run, …"
license: MIT
metadata:
  "googlecloud-plugin/version": "0.1"
  "googlecloud-plugin/triggers": "deploy to cloud run, serverless container, …"
  "googlecloud-plugin/required-scopes": "run.services.create, run.routes.invoke"
  "googlecloud-plugin/mcp-servers": "google-cloud-run"
---
```

`metadata` is specified as a map from string keys to string values, so lists are
comma-joined rather than nested. Keys are namespaced because the specification
asks authors to keep key names unique against other clients' metadata.

`required-scopes` is emitted even when empty — "this skill needs no IAM scopes"
is a claim worth making explicitly, and the security gate reads it.

## Alternatives considered

**Keep YAML lists under `metadata`.** More readable and diffable, and the
reference validator does not type-check metadata values today. Rejected: it
contradicts the specification's "string values" prose, and the plugin's entire
pitch is conformance. Passing only because the validator has a gap is not
conformance.

**Drop the fields entirely.** Leanest frontmatter, but the machine-readable IAM
scope data stops being queryable — `gcp-security` reads it to pre-check
least-privilege before a task runs.

**Keep `${GCP_PROJECT_ID}` and document the caveat.** Some clients pre-expand
their own environment. Rejected: on a strictly conformant client it actively
mis-sets the project, which is worse than not setting it at all.

## Consequences

- ✅ A conformant client loads the plugin and all 17 skills.
- ✅ Verified independently: `skills-ref` (the official reference validator)
  reports 17/17 valid; `check-jsonschema` validates both manifests against the
  published schemas.
- ✅ `make spec` enforces conformance in CI, reporting against the
  specification's own FATAL / MCP / SKILL failure boundaries.
- ✅ No breakage. `.claude-plugin/`, `.kimi-plugin/`, `gemini-extension.json`
  and `.agents/` are untouched — the specification closes the `plugin.json`
  field set and fixes component locations, but says nothing about sibling
  directories. All four harnesses remain installable.
- ⚠️ Routing now depends on description quality alone. A skill whose keywords
  are absent from its description will not be found, and no validator can catch
  that — only routing tests can.
- ⚠️ `triggers` survives in `metadata` for this plugin's own tooling, but no
  client reads it. It must be kept in sync with the description by hand, or it
  rots into a second source of truth.
- ⚠️ Agent Plugins 1.0.0 specifies no install mechanism, distribution protocol,
  permission model or sandboxing. Marketplace packaging stays harness-specific
  until a future version addresses it.
