# Status

Last updated: 2026-11-13 (release v0.4.0). What is happening now and what waits on whom. One entry per working session; pruned, not grown.

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

- `v0.4.0` ([#25](https://github.com/jpantsjoha/googlecloud-plugin/pull/25)): Developer Knowledge works in Claude Code from gcloud ADC with no API key — verified live; square logo for Codex and Kimi.
- `v0.3.0` ([#23](https://github.com/jpantsjoha/googlecloud-plugin/issues/23)): the work in the table above; ADR-008 accepted as the operator's decision (JP, 2026-11-13).

## Waiting on the operator

| # | Decision | Recommendation | Unblocks | Cost if wrong | Reversibility |
|---|---|---|---|---|---|
| 1 | Your own Claude Code Developer Knowledge server ([#25](https://github.com/jpantsjoha/googlecloud-plugin/pull/25)) | Remove it — `claude mcp remove google-developer-knowledge` — so the plugin's keyless server takes over; it currently reads the unset `GOOGLE_DEVELOPER_KNOWLEDGE_API_KEY` and every call fails with `API key not valid` | Working docs grounding in your sessions | Losing a server you re-add in one command | cheap |
| 2 | Listing re-index ([docs/SUBMISSIONS.md](docs/SUBMISSIONS.md)) | Resubmit the repo to Claude Plugin Hub so the listing shows `v0.4.0` | Directory visitors see the new skills | None | cheap |

## Not done, and why

- **No `displayName`/`logo`/`suggestedPrompts` in root `plugin.json`** ([#20](https://github.com/jpantsjoha/googlecloud-plugin/pull/20)) — Agent Plugins 1.0.0 closes it to 10 fields (schema fetched 2026-11-13). Google's own root manifest carries them anyway.
- **No `ROADMAP.md`** ([#23](https://github.com/jpantsjoha/googlecloud-plugin/issues/23)) — no further plan exists after the release.

## Open

- The remote Cloud CLI MCP is untested live ([#21](https://github.com/jpantsjoha/googlecloud-plugin/pull/21)); `cloudcli.googleapis.com` did not appear in `gcloud services list --available`. Developer Knowledge was verified live in [#25](https://github.com/jpantsjoha/googlecloud-plugin/pull/25).
- The Kimi manifest's `interface.logo` key is assumed, not checked against a Kimi schema ([#25](https://github.com/jpantsjoha/googlecloud-plugin/pull/25)).
- `make check` will report drift on `research/SOURCES.md` for the Google catalog `index.json`, which changes often ([#14](https://github.com/jpantsjoha/googlecloud-plugin/pull/14)).
