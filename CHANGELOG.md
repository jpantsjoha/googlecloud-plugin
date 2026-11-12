# Changelog

All notable changes to this plugin are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `gcloud-guardrails` skill — rules for every `gcloud` call: check the exact
  subcommand with `gcloud help`, dry-run where supported, cut output down, name
  project and location, one command per call. Read-only commands run;
  anything that creates, changes, stops, removes or bills waits for a named
  person, with a stricter denylist on top. Adapted from Google's `gcloud`
  skill (Apache-2.0). ([#13](https://github.com/jpantsjoha/googlecloud-plugin/issues/13),
  [#14](https://github.com/jpantsjoha/googlecloud-plugin/pull/14))
- `google-skills-catalog` skill — fetches at most three matching skills from
  Google's public catalog (`google/skills`) for product depth beyond this
  plugin: HTTPS only, no redirects, Google-repository entrypoints only, and
  fetched guidance ranked below user, plugin and harness rules. Adapted from
  Google's `finding-google-skills` (Apache-2.0). ([#13](https://github.com/jpantsjoha/googlecloud-plugin/issues/13),
  [#14](https://github.com/jpantsjoha/googlecloud-plugin/pull/14))
- `developer-knowledge` remote MCP server (official Google documentation) in
  `.mcp.json` (API key from `DEVELOPERKNOWLEDGE_API_KEY`), `mcp_config.json` and
  `gemini-extension.json` (Google credentials). Not in the portable `mcp.json`.
  ([#14](https://github.com/jpantsjoha/googlecloud-plugin/pull/14))
- `NOTICE` for the adapted Apache-2.0 text; ADR-008 (Proposed) records the
  decision. ([#14](https://github.com/jpantsjoha/googlecloud-plugin/pull/14))
- `CONTRIBUTING.md` — the gate, the skill contract, and why each rule exists.
- `SECURITY.md` — private reporting, and what counts as a vulnerability in a
  plugin that ships instructions rather than a running service.
- `CODE_OF_CONDUCT.md` — Contributor Covenant 2.1.
- Issue templates for incorrect GCP guidance, skills not loading or routing, and
  new-skill proposals; plus a pull-request template carrying the safety checks.

### Changed

- The packaging gate (`make manifest`) now checks that a remote MCP server's
  endpoint matches across harnesses, using each harness's own key (`url`,
  `serverUrl`, `httpUrl`), and rejects a key meant for another harness.
  ([#14](https://github.com/jpantsjoha/googlecloud-plugin/pull/14))
- `AGENTS.md` and `GEMINI.md` route every `gcloud` call through
  `gcloud-guardrails` and send product-depth questions to
  `google-skills-catalog`. ([#14](https://github.com/jpantsjoha/googlecloud-plugin/pull/14))

## [0.2.0] — 2026-08-07

**Standards release.** The plugin now conforms to
[Agent Plugins 1.0.0](https://agent-plugins.org/specification) and the
[Agent Skills specification](https://agentskills.io/specification), the open
vendor-neutral packaging standards co-maintained by Amazon, Cursor, Google,
Microsoft, OpenAI and Vercel.

Before this release, a conformant Agent Plugins client would have loaded
**nothing** from this plugin. Two independent fatal faults:

1. `plugin.json` omitted the required `$schema`. The manifest schema is closed,
   so §5.2 makes the omission fatal — the client rejects the plugin outright.
2. All 17 skills carried top-level frontmatter outside the closed Agent Skills
   field set. §6.1 requires clients to **skip** every non-conforming skill.

### Added

- `mcp.json` — the portable MCP manifest, with an explicit `stdio` transport
  discriminator.
- `make spec` — Agent Plugins 1.0.0 conformance gate, reporting against the
  specification's own failure boundaries (FATAL / MCP / SKILL).
- `scripts/validate_agent_plugins.py` — dependency-free conformance checker;
  no network call needed in CI.
- README **Standards and compliance** section, with commands to verify
  conformance without trusting this repo's own scripts.
- [ADR-007](architecture/decisions/ADR-007-agent-plugins-conformance.md) —
  the adoption decision and its trade-offs.
- `skills/mcp-servers/references/agent-plugins-mcp.md` — the placeholder-expansion
  trap, and Toolbox as a documented opt-in.
- This changelog.

### Changed

- **BREAKING (skill authors and downstream tooling).** SKILL.md frontmatter is
  reduced to `{name, description, license, metadata}`. The top-level `version`,
  `triggers`, `required_scopes`, `mcp_servers`, `persona`, `tier`, `gate` and
  `owns_eval` fields are gone. The same data is retained under `metadata`,
  namespaced and comma-joined:

  ```yaml
  metadata:
    "googlecloud-plugin/required-scopes": "run.services.create, run.services.get"
  ```

  Anything reading the old YAML lists must now read the namespaced key and split
  on `", "`.
- Routing keywords moved from `triggers` into `description` — the only field a
  conformant client routes on.
- Eight skill descriptions gained explicit boundary clauses after cross-harness
  routing tests showed four pairs where both skills matched the same request:
  `iam`↔`gcp-security`, `gcp-ops`↔`logging-monitoring`,
  `vertex-ai`↔`agent-architect`, `gcp-architect`↔`solution-designer`.
- `scripts/validate_skills.py` inverted — it now enforces the closed Agent Skills
  field set instead of requiring the fields that broke conformance.
- Smoke tests expanded from 136 to 195, covering both specifications.
- `make manifest` no longer claims the plugin is "installable across 4
  harnesses". It verifies manifests parse and agree, and now says so.

### Fixed

- `.claude/CLAUDE.md` described itself as gitignored and never committed. It is
  tracked and public; `.gitignore` covers `.claude/local-CLAUDE.md`. Corrected.
- `vertex-ai` advertised "Agent Builder" while directing agentic work elsewhere.
  Agent Builder now belongs to `agent-architect` in both descriptions.

### Compatibility

No action required for existing users. The per-harness manifests
(`.claude-plugin/`, `.kimi-plugin/`, `gemini-extension.json`, `.agents/`) are
unchanged and remain alongside the portable layout — Agent Plugins closes the
`plugin.json` field set and fixes component locations, but says nothing about
sibling directories.

`mcp.json` deliberately declares only the `gcloud` server. Toolbox needs a
user-specific `tools.yaml` path that no Agent Plugins placeholder can express,
so it stays an opt-in documented in `skills/mcp-servers/`. `mcp.json` also
declares no `env`: only `${PLUGIN_ROOT}` and `${PLUGIN_DATA}` expand, so
`CLOUDSDK_CORE_PROJECT: "${GCP_PROJECT_ID}"` would have been passed through
literally and mis-set the project. Export it in your shell instead.

### Verification

| Check | Result |
|---|---|
| `skills-ref` (official Agent Skills reference validator) | 17/17 valid |
| `check-jsonschema` vs published `plugin.schema.json` / `mcp.schema.json` | pass |
| `agy plugin validate` (Antigravity loader) | 17 skills, 2 mcpServers, exit 0 |
| Antigravity routing | 17 skills visible, 6/6 routed correctly |
| Kimi routing (`--skills-dir`) | 17 skills loaded, 7/7 routed correctly |
| Live MCP handshake | `gcloud-mcp-server` v0.5.3, protocol 2025-06-18, `run_gcloud_command` |
| `make gate` | spec + validate + manifest + mermaid + 102 URLs + 195 tests |

Not verified: Codex (usage limit at time of release) and Toolbox (opt-in).

## [0.1.0] — 2026-07-23

Initial release. Six persona skills, eleven service skills, MCP server setup,
and a self-validating research pipeline.

[0.2.0]: https://github.com/jpantsjoha/googlecloud-plugin/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/jpantsjoha/googlecloud-plugin/releases/tag/v0.1.0
