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

- `v0.5.1` — tagged when release PR [#33](https://github.com/jpantsjoha/googlecloud-plugin/pull/33) merges ([#32](https://github.com/jpantsjoha/googlecloud-plugin/pull/32)): project guard false positives fixed; README quick start, comparison and troubleshooting ([#31](https://github.com/jpantsjoha/googlecloud-plugin/pull/31)).
- `v0.5.0` ([#27](https://github.com/jpantsjoha/googlecloud-plugin/pull/27), [#29](https://github.com/jpantsjoha/googlecloud-plugin/pull/29)): project resolution from env, `.env` and gcloud config, enforced in Claude Code by a hook that asks on conflict; `gcloud` MCP no longer receives a literal `${GCP_PROJECT_ID}`; GenAI Toolbox no longer shipped.
- `v0.4.0` ([#25](https://github.com/jpantsjoha/googlecloud-plugin/pull/25)): Developer Knowledge works in Claude Code from gcloud ADC with no API key — verified live; square logo for Codex and Kimi.
- `v0.3.0` ([#23](https://github.com/jpantsjoha/googlecloud-plugin/issues/23)): the work in the table above; ADR-008 accepted as the operator's decision (JP, 2026-11-13).

## Waiting on the operator

Ordered so the one that compounds comes first: the installed v0.5.0 guard blocks ordinary commands that mention `gcloud` until v0.5.1 is installed.

| # | Decision | Recommendation | Unblocks | Cost if wrong | Reversibility |
|---|---|---|---|---|---|
| 1 | Release v0.5.1 ([#33](https://github.com/jpantsjoha/googlecloud-plugin/pull/33)) | Approve #33: merge, tag `v0.5.1`, publish the release, update the installed plugin, re-sync the Hub listing | Installed copies stop blocking commands that only mention `gcloud` ([#32](https://github.com/jpantsjoha/googlecloud-plugin/pull/32)); merging alone would publish, since installs read the version from `main` | A defective tag needs a `0.5.2`; users who updated keep it | one-way |
| 2 | OpenAI API review lane at its spend cap | Leave the cap as it is: reviews run on the Codex subscription lane, which answered every request on 2026-11-13 | Nothing, while the subscription lane has quota | Raising it spends money for no gain while the subscription lane works | cheap |

The README usage section is done ([#31](https://github.com/jpantsjoha/googlecloud-plugin/pull/31)).

Claude Plugin Hub listing last re-synced at `95d15d7` (v0.5.0 plus README, 2026-11-13): 20 skills, hooks, documentation score 100.

## Not done, and why

- **No `displayName`/`logo`/`suggestedPrompts` in root `plugin.json`** ([#20](https://github.com/jpantsjoha/googlecloud-plugin/pull/20)) — Agent Plugins 1.0.0 closes it to 10 fields (schema fetched 2026-11-13). Google's own root manifest carries them anyway.
- **No `ROADMAP.md`** ([#23](https://github.com/jpantsjoha/googlecloud-plugin/issues/23)) — no further plan exists after the release.

## Open

- The `gcloud` MCP server failed on the first Claude Code session after install and after update (2026-11-13), then connected after Claude Code's 15-minute retry cache; cause unknown — tracked in [#34](https://github.com/jpantsjoha/googlecloud-plugin/issues/34).
- The remote Cloud CLI MCP is untested live ([#21](https://github.com/jpantsjoha/googlecloud-plugin/pull/21)); `cloudcli.googleapis.com` did not appear in `gcloud services list --available`. Developer Knowledge was verified live in [#25](https://github.com/jpantsjoha/googlecloud-plugin/pull/25).
- The Kimi manifest's `interface.logo` key is assumed, not checked against a Kimi schema ([#25](https://github.com/jpantsjoha/googlecloud-plugin/pull/25)).
- `make check` will report drift on `research/SOURCES.md` for the Google catalog `index.json`, which changes often ([#14](https://github.com/jpantsjoha/googlecloud-plugin/pull/14)).
