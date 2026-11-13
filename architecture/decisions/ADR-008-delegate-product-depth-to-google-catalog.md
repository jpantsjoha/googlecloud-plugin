# ADR-008: Delegate Product Depth to Google's Catalog; Ground on Developer Knowledge

**Status:** Accepted — operator decision (JP, 2026-11-13), recorded on release [#23](https://github.com/jpantsjoha/googlecloud-plugin/issues/23)
**Date:** 2026-11-12
**Issue:** [#13](https://github.com/jpantsjoha/googlecloud-plugin/issues/13)

## Context

On 3 November 2026 Google published `google-cloud-developer` (v1.1.17) in `google/skills`: five skills, the Developer Knowledge remote MCP server, and an always-on rule that routes deep questions to a public catalog of 187 product skills (42 `gke-*`, 15 `agent-platform-*`, 5 `google-cloud-waf-*`).

This plugin's value is the operating contract — personas, the sequential gate, safe-by-default execution — plus first-wave service depth kept current by the research pipeline. Copying Google's product skills would multiply what that pipeline must track; ignoring them leaves depth on the table.

ADR-004 required dry runs and confirmation for billable or destructive actions, but at the time only `skills/bigquery` applied those patterns to its commands.

## Decision

1. **Command-level safety is its own skill.** `gcloud-guardrails` applies to every `gcloud` call regardless of which skill proposed it: leaf `gcloud help` validation, dry run, data reduction, explicit scoping, single commands, and a denylist that requires human authorisation.
2. **Product depth is fetched, not copied.** `google-skills-catalog` fetches, verifies and follows at most three matching catalog skills per request. Gate rules win on any conflict.
3. **Documentation grounding ships with the plugin.** `developer-knowledge` is declared in the three harness manifests (`.mcp.json`, `mcp_config.json`, `gemini-extension.json`) and excluded from the portable `mcp.json`, because it needs an API key or client-managed ADC and Agent Plugins 1.0.0 expands neither (consistent with ADR-007).
4. **The packaging drift guard compares remote endpoints.** `validate_plugin.py` reads each harness's native endpoint key (Claude `url`, Antigravity `serverUrl`, Gemini `httpUrl`), rejects another harness's spelling, and fails when a remote server's endpoint differs between harnesses. Auth fields are not compared; they differ by design.
5. **Attribution.** Adapted text keeps Google's Apache-2.0 notice in `NOTICE`; Google's usage-attribution tags are not adopted.

## Consequences

- ✅ ADR-004 becomes enforceable at the command, not only in examples.
- ✅ Depth for 180+ products without adding them to the research pipeline.
- ✅ Platform facts can be checked against live docs at run time.
- ⚠️ Catalog skills are third-party text fetched at run time. Controls: HTTPS-only fetches with no redirects, an entrypoint origin allowlist (`raw.githubusercontent.com/google/skills/main/`), and fetched guidance ranked below user, plugin and harness safety rules.
- ⚠️ Claude Code users need `DEVELOPERKNOWLEDGE_API_KEY`. Without it the server is configured with an empty key, so its calls are expected to fail authentication (not verified against the live endpoint); no other server or skill depends on it.
- ⚠️ `research/SOURCES.md` now hashes `index.json`, which changes often; `make check` will report drift on it routinely.
