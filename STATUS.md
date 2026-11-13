# Status

Last updated: 2026-11-13. What is happening now and what waits on whom. One entry per working session; pruned, not grown.

## 2026-11-13 — Google `google-cloud-developer` borrow, follow-ups landed

All items from [#13](https://github.com/jpantsjoha/googlecloud-plugin/issues/13) and its follow-ups are merged to `main`. For each PR, the pre-commit hook ran `make gate` on its final commit, and a fresh Codex Sol 6.1 reviewer (API lane) returned PASS on that exact head before merge. The review reports are kept locally by the operator's session, not posted to the PRs.

| Issue | PR | Reviewed head | Merge | What |
|---|---|---|---|---|
| [#13](https://github.com/jpantsjoha/googlecloud-plugin/issues/13) | [#14](https://github.com/jpantsjoha/googlecloud-plugin/pull/14) | `05c322d` | `5509cf1` | `gcloud-guardrails`, `google-skills-catalog`, Developer Knowledge MCP |
| [#13](https://github.com/jpantsjoha/googlecloud-plugin/issues/13) | [#18](https://github.com/jpantsjoha/googlecloud-plugin/pull/18) | `e254a29` | `313e86c` | CHANGELOG for #14 |
| [#16](https://github.com/jpantsjoha/googlecloud-plugin/issues/16) | [#19](https://github.com/jpantsjoha/googlecloud-plugin/pull/19) | `f932cd8` | `3678964` | Keyless auth patterns; key-file guard test |
| [#17](https://github.com/jpantsjoha/googlecloud-plugin/issues/17) | [#20](https://github.com/jpantsjoha/googlecloud-plugin/pull/20) | `8092be3` | `5eb915c` | Codex plugin manifest; stricter skills-path validation |
| [#15](https://github.com/jpantsjoha/googlecloud-plugin/issues/15) | [#21](https://github.com/jpantsjoha/googlecloud-plugin/pull/21) | `abc93e0` | `a4180b4` | Opt-in remote Cloud CLI MCP; MCP endpoint allowlist in link checker |

Gate on `a4180b4`: 273 tests pass, 19/19 skills conform, 4 harness manifests agree.

## Waiting on the operator

Ordered so that each decision feeds the next: settle the ADR and prove the docs server works, then release; the logo can follow the release.

| # | Decision | Recommendation | Unblocks | Cost if wrong | Reversibility |
|---|---|---|---|---|---|
| 1 | ADR-008 status ([#14](https://github.com/jpantsjoha/googlecloud-plugin/pull/14)) | Accept ADR-008: the decisions it records have shipped and passed review | A release that carries no Proposed ADR | Accepting a decision you would have shaped differently; amend by a later ADR | cheap |
| 2 | Developer Knowledge key variable ([#14](https://github.com/jpantsjoha/googlecloud-plugin/pull/14)) | Export `DEVELOPERKNOWLEDGE_API_KEY` (the name Google's plugin uses) and smoke-test the server; your user-scope server reads `GOOGLE_DEVELOPER_KNOWLEDGE_API_KEY` | Live evidence for the one shipped server that is untested, before it goes out in a release | A dead or duplicated server in your own setup only | cheap |
| 3 | Release ([#23](https://github.com/jpantsjoha/googlecloud-plugin/issues/23)) | Approve #23: bump to `0.3.0`, tag `v0.3.0`, publish the release | Existing Claude Code and Antigravity installs, assumed (not tested) to update only on a version change | A defective tag needs a `0.3.1`; users who updated keep it | one-way |
| 4 | Plugin logo ([#20](https://github.com/jpantsjoha/googlecloud-plugin/pull/20)) | Supply a square SVG for `.codex-plugin/plugin.json` and the Kimi manifest | A listing icon on Codex and Kimi | None beyond a missing icon | cheap |

## Not done, and why

- **No tag, release or version bump** ([#23](https://github.com/jpantsjoha/googlecloud-plugin/issues/23)) — release is the operator's call.
- **ADR-008 not accepted** ([#14](https://github.com/jpantsjoha/googlecloud-plugin/pull/14)) — the author does not approve its own ADR, and no delegation covers this project.
- **No `displayName`/`logo`/`suggestedPrompts` in root `plugin.json`** ([#20](https://github.com/jpantsjoha/googlecloud-plugin/pull/20)) — Agent Plugins 1.0.0 closes it to 10 fields (schema fetched 2026-11-13). Google's own root manifest carries them anyway.
- **No `ROADMAP.md`** ([#23](https://github.com/jpantsjoha/googlecloud-plugin/issues/23)) — no further plan exists beyond the release.

## Open

- Live behaviour of both remote MCP servers is untested ([#14](https://github.com/jpantsjoha/googlecloud-plugin/pull/14), [#21](https://github.com/jpantsjoha/googlecloud-plugin/pull/21)): with no API key, the Developer Knowledge server is expected to reject calls; `cloudcli.googleapis.com` did not appear in `gcloud services list --available`.
- `make check` will report drift on `research/SOURCES.md` for the Google catalog `index.json`, which changes often ([#14](https://github.com/jpantsjoha/googlecloud-plugin/pull/14)).
