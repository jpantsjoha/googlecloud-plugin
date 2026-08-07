# Contributing

Thanks for considering a contribution. This plugin installs a Google Cloud
delivery team into other people's coding agents, so the bar is the same as any
production dependency: if a skill gives bad GCP advice, someone deploys it.

## Before you start

Open an issue first for anything beyond a typo. A new skill in particular is
worth discussing — the plugin is **GCP-only and opinionated by design**, and not
every service warrants one.

## Setup

```bash
git clone https://github.com/jpantsjoha/googlecloud-plugin.git
cd googlecloud-plugin
pip install pyyaml pytest
make hooks     # installs the pre-commit hook that runs `make gate`
```

## The gate

Everything must pass before a PR can merge. CI runs the same checks.

```bash
make gate
```

| Target | What it checks |
|---|---|
| `make spec` | Agent Plugins 1.0.0 conformance — `plugin.json`, `mcp.json`, `skills/` layout |
| `make validate` | Every `SKILL.md` against the Agent Skills specification |
| `make manifest` | The four per-harness manifests parse and agree |
| `make mermaid` | Diagrams render safely on GitHub |
| `make lint` | Every reference URL resolves (HTTP 200) |
| `make test` | Smoke tests |

`make lint` hits ~100 live URLs. If you get HTTP 429 you have been rate-limited —
wait, don't "fix" the links. CI runs from a different address.

## Standards this plugin conforms to

Two open, vendor-neutral specifications, both enforced in CI:

- [Agent Plugins 1.0.0](https://agent-plugins.org/specification)
- [Agent Skills](https://agentskills.io/specification)

Verify against the upstream tooling rather than trusting our scripts:

```bash
uvx --from "git+https://github.com/agentskills/agentskills.git#subdirectory=skills-ref" \
    skills-ref validate skills/cloud-run
uvx check-jsonschema \
    --schemafile https://agent-plugins.org/schemas/1.0.0/plugin.schema.json plugin.json
```

## Writing a skill

Each skill is `skills/<name>/SKILL.md` plus a `references/` directory.

**The frontmatter field set is closed.** Only `name`, `description`, `license`,
`compatibility`, `allowed-tools` and `metadata` are permitted. Add anything else
at the top level and a conformant client **must skip your skill entirely** — it
will not error, it will silently not load. Everything specific to this plugin is
namespaced under `metadata` as **string** values:

```yaml
---
name: cloud-run
description: "Deploy and manage containerized workloads on Cloud Run. … Use when the user mentions: deploy to cloud run, serverless container, …"
license: MIT
metadata:
  "googlecloud-plugin/version": "0.1"
  "googlecloud-plugin/triggers": "deploy to cloud run, serverless container"
  "googlecloud-plugin/required-scopes": "run.services.create, run.services.get"
  "googlecloud-plugin/mcp-servers": "google-cloud-run"
---
```

Three rules the validator enforces, each of which exists because it broke once:

1. **`description` is the only thing a conformant client routes on.** It must say
   what the skill does *and* when to use it, ending with
   `Use when the user mentions: …`.
2. **Every trigger in `metadata` must appear in `description`.** A trigger
   recorded only in metadata is unroutable — nothing reads metadata — so it rots
   silently while looking like coverage.
3. **Where two skills overlap, each must name the other and draw the line.**
   `Use this to author or change IAM; use gcp-security instead to audit an
   existing posture.` Without it, both match and routing is a coin flip.

Keep `SKILL.md` under 500 lines. Move detail into `references/`, which agents
load on demand.

## Safety rules — non-negotiable

These are why the plugin exists. A PR that breaks one will be rejected.

- **No credential values anywhere.** Reference the location, never the secret.
- **Every billable action carries a cost warning** before the command.
- **No `roles/owner` or `roles/editor`** in any example. Least privilege, always.
- **No public Cloud Storage buckets** without explicit, stated design intent.
- **No `--allow-unauthenticated` Cloud Run** without a security rationale.

## Sources must be real and current

Every technical claim needs a live Google Cloud reference. No invented flags, no
half-remembered API shapes — check the docs and cite them. `make check` detects
when a cited page has drifted since it was captured.

## Pull requests

- Branch from `main`: `feat/description` or `fix/description`. `main` is
  protected; PRs are required.
- One logical change per PR.
- Explain **why**, not just what. The diff shows what.
- Update `CHANGELOG.md` under `[Unreleased]` for anything user-facing.
- Add an ADR in `architecture/decisions/` for a significant decision.
- Update `research/coverage-matrix.md` when a skill's status changes.

## Reporting problems

- **Wrong GCP guidance** — please open an issue. Incorrect advice is the worst
  failure mode this plugin has, more serious than any crash.
- **Security issue** — see [SECURITY.md](SECURITY.md). Don't open a public issue.

## Licence

Contributions are MIT, matching the project.
