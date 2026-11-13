# Submission Targets

Where to list `googlecloud-plugin` so builders can find and install it. Each entry has the destination, what it needs, and the status.

> **Standards note.** This plugin is compliant with [Agent Plugins 1.0.0](https://agent-plugins.org/specification)
> and the [Agent Skills specification](https://agentskills.io/specification) — the vendor-neutral standards
> ([announcement](https://developers.googleblog.com/agent-plugins-package-your-skills-tools-and-more/)).
> Directory-layout advice written for a single client is a *subset* of what we ship: the per-harness manifests
> stay alongside the portable `plugin.json` + `mcp.json`. Never add client-specific keys to SKILL.md frontmatter
> (e.g. `when_to_use`) — the Agent Skills field set is closed and a conformant client MUST skip a skill that
> carries extras.

## 1. Claude Plugin Hub — primary (Claude Code)

- **Where:** https://www.claudepluginhub.com
- **Needs:** a public repo with `.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json` (both present). Submit the repo URL.
- **Precedent:** `devex-charter` (formerly `join-the-team`) is listed here: <https://www.claudepluginhub.com/plugins/jpantsjoha-devex-charter>.
- **Install string once listed:**
  ```
  /plugin marketplace add jpantsjoha/googlecloud-plugin
  /plugin install googlecloud-plugin@googlecloud-plugin-marketplace
  ```
- **Re-index:** the hub auto-discovers on a schedule (GitHub Code Search backed), but submitting the repo URL
  at https://www.claudepluginhub.com is the fastest route. Its own guide: *"Push your plugin to GitHub and
  submit the URL for the fastest route to indexing."*
- **Status:** **LISTED** and verified owner. Showing v0.1.0 as of 2026-08-07 — awaiting re-crawl of the
  v0.2.0 release. No self-service refresh control exists on the listing page.

## 2. Gemini CLI Extensions — Antigravity / Gemini

- **Where:** https://github.com/gemini-cli-extensions (community extensions org; `gcloud-mcp`, `dak` live here)
- **Needs:** `gemini-extension.json` (present) with `contextFileName` + inline `mcpServers` (present). Open a PR / request listing per that org's contribution guide.
- **Install once listed:**
  ```
  agy plugin install https://github.com/jpantsjoha/googlecloud-plugin
  ```
- **Status:** validated locally (`agy plugin validate .` → 17 skills + 2 mcpServers). Ready to request listing.

## 3. Anthropic official marketplace — canonical Claude listing

- **Where:** https://claude.ai/settings/plugins/submit or https://platform.claude.com/plugins/submit
- **Needs:** public repo with `.claude-plugin/plugin.json` + `marketplace.json` (both present and valid).
- **Note:** complementary to Claude Plugin Hub, not competing — per the hub's own guidance.
- **Status:** not yet submitted. Eligible now that v0.2.0 is tagged and released.

## 4. awesome-claude-code — community list

- **Where:** https://github.com/hesreallyhim/awesome-claude-code
- **Needs:** a PR adding the repo under the plugins/skills section, one-line description.
- **Status:** ready — draft the PR entry.

## 5. MCP servers registry — optional (MCP angle)

- **Where:** https://github.com/modelcontextprotocol/servers
- **Needs:** only relevant if we surface the bundled MCP setup as a standalone entry; the plugin mainly *consumes* MCP servers rather than *being* one. Low priority.
- **Status:** optional.

## Pre-submission checklist

- [x] Public repo, MIT licensed
- [x] `.claude-plugin/plugin.json` + `marketplace.json` valid
- [x] `gemini-extension.json` valid; `agy plugin validate .` passes
- [x] `.kimi-plugin/plugin.json` + `AGENTS.md` (Codex) present
- [x] README with install blocks for all four harnesses
- [x] Repo description + 20 topics set
- [x] `make gate` green in CI (gate.yml)
- [x] "Not affiliated with Google" disclaimer in README
- [x] Tag a release before submitting — `v0.2.0` tagged and released 2026-08-07
- [x] Conforms to Agent Plugins 1.0.0 (`make spec`) and Agent Skills (`skills-ref` 17/17)
- [x] `CHANGELOG.md` present; version bumped so clients invalidate their cache
- [ ] Submit repo URL to Claude Plugin Hub to trigger re-index of v0.5.0
- [ ] Submit to Anthropic official marketplace
