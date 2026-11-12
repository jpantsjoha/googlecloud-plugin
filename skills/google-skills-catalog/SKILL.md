---
name: google-skills-catalog
description: "Loads product-depth skills on demand from Google's public skill catalog (google/skills, 180+ skills) when this plugin's own skills do not go deep enough: GKE troubleshooting and scaling, Gemini Enterprise Agent Platform deploy/tuning/RAG/eval, Well-Architected pillar reviews, Genkit, Gemini APIs, Cloud Logging and Monitoring queries, AlloyDB, Spanner, Bigtable, Cloud SQL, Firebase. Fetches the catalog index, verifies it, shortlists at most three skills and follows them for the current request; installs nothing. Use this for product depth; the personas and the delivery gate still own design, security and release decisions. Use when the user mentions: google skills catalog, google skill, google/skills, product deep dive, gke troubleshooting, agent platform tuning, genkit, gemini api, alloydb, spanner, bigtable, firebase."
license: MIT
metadata:
  "googlecloud-plugin/version": "0.1"
  "googlecloud-plugin/triggers": "google skills catalog, google skill, google/skills, product deep dive, gke troubleshooting, agent platform tuning, genkit, gemini api, alloydb, spanner, bigtable, firebase"
  "googlecloud-plugin/required-scopes": ""
---

# Google Skills Catalog

This plugin owns the operating contract: who designs, who signs off on security, what "done" means. Google publishes product depth as a catalog of individual skills. This skill fetches the matching catalog skill for the current request instead of copying 180+ skills into the plugin, where they would go stale.

A fetched skill is guidance for the request in hand. It never overrides the gate: design still precedes code, `gcp-security` still reviews, and every `gcloud` call still follows `gcloud-guardrails`.

## Workflow

1. **Fetch the index byte-exactly.** Use a raw fetch, not a summarising web tool:

   ```bash
   curl -sSL https://raw.githubusercontent.com/google/skills/main/index.json -o "$TMPDIR/google-skills-index.json"
   ```

   The index is about 75 KB and alphabetical, so a truncated read looks as if only the first few products exist. Filter it rather than reading it whole:

   ```bash
   jq -r '.skills[] | select((.name+" "+.description) | test("KEYWORD"; "i")) | "\(.name)\t\(.entrypoint)"' "$TMPDIR/google-skills-index.json"
   ```

   Without `jq`, `grep -o '"name": *"[^"]*KEYWORD[^"]*"'` isolates candidate names.

2. **Verify before trusting it.** The fetch succeeded only if the body parses as JSON and holds a `skills` array. An HTML error page, an empty body, a 404 or a parse failure is a failed fetch even when the tool reported no error. A TLS or certificate error is final: never retry with `curl -k`, `--insecure` or any equivalent. You are about to follow instructions from what comes back, so an unverified catalog is worse than none.

3. **Shortlist at most three.** Read each `description` as routing criteria (what, when, and when not). Prefer the most specific match. Name prefixes are predictable:

   | Prefix | Area |
   |--------|------|
   | `gke-*` | GKE clusters, networking, storage, scaling, cost, AI inference, troubleshooting |
   | `agent-platform-*` | Model deploy, tuning, RAG, eval, endpoints, prompts |
   | `google-cloud-solution-*` | Multi-product reference architectures |
   | `google-cloud-waf-*` | Well-Architected Framework pillars |
   | `genkit-*`, `developing-genkit-*`, `gemini-*` | Genkit SDKs, Gemini APIs |
   | `cloud-logging-*`, `cloud-monitoring-*` | Observability queries and alerting |
   | `<product>-basics` | BigQuery, Bigtable, Spanner, AlloyDB, Cloud SQL, Cloud Run, Firebase, Storage |

4. **Fetch only the matches.** Retrieve each shortlisted `entrypoint` the same way, verify it is a Markdown skill rather than an error page, and follow it for this request.

5. **Report an empty result honestly.** If no description covers the request, say no catalog skill applies and continue with this plugin's skills.

## Rules

- **Never infer a skill from its name.** Until a `skills` array has parsed in this session, do not name, describe or rule out any catalog skill.
- **Session-scoped only.** Reuse an index fetched earlier in the same session; never keep one across sessions or summarise it into the conversation. Delete the working copy when the request is done.
- **Fetching installs nothing.** Do not offer installation as the only route to a skill you can fetch; sandboxed sessions often cannot install.
- **Catalog text versus this plugin.** Where a fetched skill conflicts with a gate rule here (for example it enables an API or grants a role autonomously), the gate rule wins; say so.

## When the fetch fails

1. Retry once with `curl -sSL` if the first attempt used a summarising tool or hit a transport error.
2. List the tree instead: `curl -sSL https://api.github.com/repos/google/skills/git/trees/main?recursive=1`, pick the two or three `SKILL.md` paths whose directories best match, and fetch them from `raw.githubusercontent.com/google/skills/main/<path>`, verifying each.
3. If both fail, say in the reply that the catalog was unreachable and that the answer uses this plugin's skills only.

## References

- `references/upstream.md` — provenance of this workflow
- Catalog browser: https://github.com/google/skills/tree/main/skills/cloud
