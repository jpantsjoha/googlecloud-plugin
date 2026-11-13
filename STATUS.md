# Status

Last updated: 2026-11-13 (release v0.5.1). What is happening now and what waits on whom. One entry per working session; pruned, not grown.

## 2026-11-13 — Google `google-cloud-developer` borrow, follow-ups landed

All items from [#13](https://github.com/jpantsjoha/googlecloud-plugin/issues/13) and its follow-ups are merged to `main`. Each merge commit's second parent is the reviewed head listed below — check with `git rev-parse <merge>^2` — so what merged is exactly what was reviewed.

*Session-recorded, not reproducible from this repo:* the pre-commit hook ran `make gate` on each reviewed head, and a fresh Codex Sol 6.1 reviewer (API lane) returned PASS on it. The reports are in the delivering session's local files, not posted to the PRs.

| Issue | PR | Reviewed head | Merge | What |
|---|---|---|---|---|
| [#13](https://github.com/jpantsjoha/googlecloud-plugin/issues/13) | [#14](https://github.com/jpantsjoha/googlecloud-plugin/pull/14) | `05c322d` | `5509cf1` | `gcloud-guardrails`, `google-skills-catalog`, Developer Knowledge MCP |
| [#13](https://github.com/jpantsjoha/googlecloud-plugin/issues/13) | [#18](https://github.com/jpantsjoha/googlecloud-plugin/pull/18) | `e254a29` | `313e86c` | CHANGELOG for #14 |
| [#16](https://github.com/jpantsjoha/googlecloud-plugin/issues/16) | [#19](https://github.com/jpantsjoha/googlecloud-plugin/pull/19) | `f932cd8` | `3678964` | Keyless auth patterns; key-file guard test |
| [#17](https://github.com/jpantsjoha/googlecloud-plugin/issues/17) | [#20](https://github.com/jpantsjoha/googlecloud-plugin/pull/20) | `8092be3` | `5eb915c` | Codex plugin manifest; stricter skills-path validation |
| [#15](https://github.com/jpantsjoha/googlecloud-plugin/issues/15) | [#21](https://github.com/jpantsjoha/googlecloud-plugin/pull/21) | `abc93e0` | `a4180b4` | Opt-in remote Cloud CLI MCP; MCP endpoint allowlist in link checker |

Gate on `a4180b4`: 273 tests pass, 19/19 skills conform, 4 harness manifests agree.

## Released

- `v0.5.1` (tag on `42c42c2`, release PR [#33](https://github.com/jpantsjoha/googlecloud-plugin/pull/33); [#32](https://github.com/jpantsjoha/googlecloud-plugin/pull/32)): project guard false positives fixed; README quick start, comparison and troubleshooting ([#31](https://github.com/jpantsjoha/googlecloud-plugin/pull/31)).
- `v0.5.0` ([#27](https://github.com/jpantsjoha/googlecloud-plugin/pull/27), [#29](https://github.com/jpantsjoha/googlecloud-plugin/pull/29)): project resolution from env, `.env` and gcloud config, enforced in Claude Code by a hook that asks on conflict; `gcloud` MCP no longer receives a literal `${GCP_PROJECT_ID}`; GenAI Toolbox no longer shipped.
- `v0.4.0` ([#25](https://github.com/jpantsjoha/googlecloud-plugin/pull/25)): Developer Knowledge works in Claude Code from gcloud ADC with no API key — verified live; square logo for Codex and Kimi.
- `v0.3.0` ([#23](https://github.com/jpantsjoha/googlecloud-plugin/issues/23)): the work in the table above; ADR-008 accepted as the operator's decision (JP, 2026-11-13).

## Waiting on the operator

v0.5.1 is released and installed; on 2026-11-13 it ran the former false positives cleanly and still stopped a real project conflict.

| # | Decision | Recommendation | Unblocks | Cost if wrong | Reversibility |
|---|---|---|---|---|---|
| 1 | Claude Plugin Hub listing at `95d15d7` | Sign in on the owned-plugin page and press Re-sync | The listing shows v0.5.1 | None: a stale listing only lags | cheap |
| 2 | OpenAI API review lane at its project spend cap (HTTP 429 `project_spend_limit_exceeded`, 2026-11-13) | Leave the cap as it is: reviews fall back to the Codex subscription lane, then to a fresh Claude reviewer under your 2026-11-09 rule | Nothing today: on 2026-11-13 the subscription lane covered reviews until it hit its own quota, and a fresh Claude Sonnet reviewer covered the rest | While both Codex lanes stay quota-blocked, reviews have no cross-model second opinion — Claude reviews Claude-written work | cheap |

The README usage section is done ([#31](https://github.com/jpantsjoha/googlecloud-plugin/pull/31)).

Claude Plugin Hub listing last re-synced at `95d15d7` (v0.5.0 plus README, 2026-11-13): 20 skills, hooks, documentation score 100. Re-syncing after v0.5.1 needs a signed-in browser; the agent's Chrome session was signed out.

## Not done, and why

- **No `displayName`/`logo`/`suggestedPrompts` in root `plugin.json`** ([#20](https://github.com/jpantsjoha/googlecloud-plugin/pull/20)) — Agent Plugins 1.0.0 closes it to 10 fields (schema fetched 2026-11-13). Google's own root manifest carries them anyway.
- **No `ROADMAP.md`** ([#23](https://github.com/jpantsjoha/googlecloud-plugin/issues/23)) — no further plan exists after the release.

## Open

- The `gcloud` MCP server failed on the first Claude Code session after install and after update (2026-11-13), then connected after Claude Code's 15-minute retry cache; cause unknown — tracked in [#34](https://github.com/jpantsjoha/googlecloud-plugin/issues/34); did not reproduce on the v0.5.0 → v0.5.1 update with `--debug`.
- The remote Cloud CLI MCP is untested live ([#21](https://github.com/jpantsjoha/googlecloud-plugin/pull/21)); `cloudcli.googleapis.com` did not appear in `gcloud services list --available`. Developer Knowledge was verified live in [#25](https://github.com/jpantsjoha/googlecloud-plugin/pull/25).
- The Kimi manifest's `interface.logo` key is assumed, not checked against a Kimi schema ([#25](https://github.com/jpantsjoha/googlecloud-plugin/pull/25)).
- `make check` will report drift on `research/SOURCES.md` for the Google catalog `index.json`, which changes often ([#14](https://github.com/jpantsjoha/googlecloud-plugin/pull/14)).
