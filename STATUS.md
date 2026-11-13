# Status

Last updated: 2026-11-13. What is happening now and what waits on whom. One entry per working session; pruned, not grown.

## 2026-11-13 — Google `google-cloud-developer` borrow, follow-ups landed

All items from [#13](https://github.com/jpantsjoha/googlecloud-plugin/issues/13) and its follow-ups are merged to `main`. Each PR passed `make gate` locally and an independent review (Codex Sol 6.1, API lane) before merge.

| Issue | PR | Merge | What |
|---|---|---|---|
| [#13](https://github.com/jpantsjoha/googlecloud-plugin/issues/13) | [#14](https://github.com/jpantsjoha/googlecloud-plugin/pull/14) | `5509cf1` | `gcloud-guardrails`, `google-skills-catalog`, Developer Knowledge MCP |
| — | [#18](https://github.com/jpantsjoha/googlecloud-plugin/pull/18) | `313e86c` | CHANGELOG for #14 |
| [#16](https://github.com/jpantsjoha/googlecloud-plugin/issues/16) | [#19](https://github.com/jpantsjoha/googlecloud-plugin/pull/19) | `3678964` | Keyless auth patterns; key-file guard test |
| [#17](https://github.com/jpantsjoha/googlecloud-plugin/issues/17) | [#20](https://github.com/jpantsjoha/googlecloud-plugin/pull/20) | `5eb915c` | Codex plugin manifest; stricter skills-path validation |
| [#15](https://github.com/jpantsjoha/googlecloud-plugin/issues/15) | [#21](https://github.com/jpantsjoha/googlecloud-plugin/pull/21) | `a4180b4` | Opt-in remote Cloud CLI MCP; MCP endpoint allowlist in link checker |

Gate on `a4180b4`: 273 tests pass, 19/19 skills conform, 4 harness manifests agree.

## Waiting on the operator

| # | Decision | Recommendation | Unblocks | Cost if wrong | Reversibility |
|---|---|---|---|---|---|
| 1 | Release the work above | Bump every manifest and `scripts/validate_plugin.py` to `0.3.0`, move `[Unreleased]` to `[0.3.0]`, tag `v0.3.0` and publish the release | Existing Claude Code and Antigravity installs, which key on the `0.2.0` version (assumed, not tested) | A tag with a defect needs a `0.3.1`; users who updated keep it | one-way |
| 2 | ADR-008 status ([#14](https://github.com/jpantsjoha/googlecloud-plugin/pull/14)) | Accept it: the decisions it records have shipped and passed review | Retires the last Proposed ADR | Accepting a decision you would have shaped differently; amend by a later ADR | cheap |
| 3 | Developer Knowledge key variable | Keep `DEVELOPERKNOWLEDGE_API_KEY` (matches Google's plugin) and export it in your shell; your user-scope server uses `GOOGLE_DEVELOPER_KNOWLEDGE_API_KEY` | Plugin's Developer Knowledge server working in your Claude Code | Two servers or a dead one in your own setup only | cheap |
| 4 | Plugin logo | Supply a square SVG to add to `.codex-plugin/plugin.json` and the Kimi manifest | Listing icon on Codex/Kimi | None beyond a missing icon | cheap |

## Not done, and why

- **No tag, release or version bump** — release is the operator's call (decision 1).
- **ADR-008 not accepted** — the author does not approve its own ADR; ADR acceptance has been delegated for another project only.
- **No `displayName`/`logo`/`suggestedPrompts` in root `plugin.json`** — Agent Plugins 1.0.0 closes it to 10 fields. Google's own root manifest carries them anyway.
- **No `ROADMAP.md`** — no further plan exists beyond decision 1.

## Open

- Live behaviour of both remote MCP servers is untested: with no API key, the Developer Knowledge server is expected to reject calls; `cloudcli.googleapis.com` did not appear in `gcloud services list --available`.
- `make check` will report drift on `research/SOURCES.md` for the Google catalog `index.json`, which changes often.
