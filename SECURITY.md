# Security Policy

## Reporting a vulnerability

Report privately via
[GitHub Security Advisories](https://github.com/jpantsjoha/googlecloud-plugin/security/advisories/new).
Please don't open a public issue.

Expect an acknowledgement within a few days. If the report is valid you'll be
credited in the fix, unless you'd rather not be.

## What counts as a vulnerability here

This plugin ships no runtime service. It ships **instructions an agent will
follow** and **MCP server declarations an agent will launch**. The interesting
attack surface follows from that:

- A skill that instructs an agent toward an insecure configuration — over-broad
  IAM, a public bucket, an unauthenticated endpoint, a disabled control.
- A prompt-injection vector in skill or reference content that could redirect an
  agent's behaviour.
- An `mcp.json` or harness manifest declaration that could execute something
  unintended, or a supply-chain concern in a declared package.
- Any credential, token, or private endpoint committed to the repository.

Incorrect-but-not-dangerous GCP guidance isn't a security issue — please file it
as [Incorrect GCP guidance](https://github.com/jpantsjoha/googlecloud-plugin/issues/new?template=incorrect-gcp-guidance.yml)
instead. It still matters; it just doesn't need private handling.

## What this plugin does with your credentials

Nothing. It never asks for, stores, or transmits a credential.

Authentication is delegated entirely to Application Default Credentials on your
own machine — `gcloud auth application-default login`. The `gcloud` MCP server
declared in `mcp.json` runs locally and inherits your ambient environment; it is
[`@google-cloud/gcloud-mcp`](https://www.npmjs.com/package/@google-cloud/gcloud-mcp),
published by Google.

`mcp.json` deliberately declares no `env` block. Under
[Agent Plugins 1.0.0](https://agent-plugins.org/specification) only
`${PLUGIN_ROOT}` and `${PLUGIN_DATA}` are expanded — any other `${...}` is passed
through literally, so an env placeholder would be actively misleading rather than
useful.

## Safety rules enforced in review

Every contribution is checked against these. They're in
[CONTRIBUTING.md](CONTRIBUTING.md) too, because they're the point of the plugin:

- No credential values anywhere — reference the location, never the secret.
- No `roles/owner` or `roles/editor` in any example.
- No public Cloud Storage buckets without explicit, stated design intent.
- No `--allow-unauthenticated` Cloud Run without a security rationale.
- Every billable action carries a cost warning before the command.

## Supported versions

The latest release on `main` is supported. Fixes ship forward rather than being
backported.
