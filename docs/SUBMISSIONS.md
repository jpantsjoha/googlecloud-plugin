# Submission Targets

Where to list `googlecloud-plugin` so builders can find and install it. Each entry has the destination, what it needs, and the status.

## 1. Claude Plugin Hub — primary (Claude Code)

- **Where:** https://www.claudepluginhub.com
- **Needs:** a public repo with `.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json` (both present). Submit the repo URL.
- **Precedent:** `join-the-team` is listed here.
- **Install string once listed:**
  ```
  /plugin marketplace add jpantsjoha/googlecloud-plugin
  /plugin install googlecloud-plugin@googlecloud-plugin-marketplace
  ```
- **Status:** ready to submit.

## 2. Gemini CLI Extensions — Antigravity / Gemini

- **Where:** https://github.com/gemini-cli-extensions (community extensions org; `gcloud-mcp`, `dak` live here)
- **Needs:** `gemini-extension.json` (present) with `contextFileName` + inline `mcpServers` (present). Open a PR / request listing per that org's contribution guide.
- **Install once listed:**
  ```
  agy plugin install https://github.com/jpantsjoha/googlecloud-plugin
  ```
- **Status:** validated locally (`agy plugin validate .` → 17 skills + 2 mcpServers). Ready to request listing.

## 3. awesome-claude-code — community list

- **Where:** https://github.com/hesreallyhim/awesome-claude-code
- **Needs:** a PR adding the repo under the plugins/skills section, one-line description.
- **Status:** ready — draft the PR entry.

## 4. MCP servers registry — optional (MCP angle)

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
- [ ] Tag a release (`v0.1.0`) before submitting
