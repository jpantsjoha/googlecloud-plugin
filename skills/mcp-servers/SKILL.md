---
name: mcp-servers
description: "Configure, install, and maintain Google-managed and self-hosted MCP servers for GCP. Covers setup, auth (ADC and service-account impersonation), capability map, troubleshooting, and version tracking. Every MCP entry includes a gcloud CLI fallback. Use when the user mentions: MCP setup, google MCP, model context protocol GCP, MCP install, MCP auth, genai toolbox, MCP tools GCP, configure MCP, developer knowledge."
license: MIT
metadata:
  "googlecloud-plugin/version": "0.1"
  "googlecloud-plugin/triggers": "MCP server, MCP setup, google MCP, model context protocol GCP, MCP install, MCP auth, genai toolbox, MCP tools GCP, configure MCP, developer knowledge"
  "googlecloud-plugin/required-scopes": ""
  "googlecloud-plugin/mcp-servers": "developer-knowledge, google-cloud-run, google-bigquery, google-gke, google-storage, google-vertex-ai, google-iam, google-logging, google-monitoring"
---

# MCP Servers — Google Cloud

Configure and maintain Model Context Protocol (MCP) servers for Google Cloud. All auth flows through ADC, optionally impersonating a service account — no downloaded keys, no credential values stored anywhere.

## Auth Architecture

All GCP MCP servers authenticate via Application Default Credentials (ADC):

```bash
# Authenticate locally (developer machine)
gcloud auth application-default login

# Act as a service account (agent or automation) — no key file
gcloud auth application-default login --impersonate-service-account=SA@PROJECT.iam.gserviceaccount.com
```

CI outside Google Cloud uses Workload Identity Federation instead. See `shared/auth/README.md` for both patterns and the key-file exception.

## What the plugin ships vs what you opt into

The portable `mcp.json` (Agent Plugins 1.0.0) declares **one** server — `gcloud`
— because that is the only one that starts with no user-supplied configuration:

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
  "mcpServers": {
    "gcloud": { "type": "stdio", "command": "npx", "args": ["-y", "@google-cloud/gcloud-mcp"] }
  }
}
```

Two consequences worth knowing:

- **No `env` block.** Agent Plugins expands only `${PLUGIN_ROOT}` and
  `${PLUGIN_DATA}`. A `${GCP_PROJECT_ID}` placeholder would be passed through
  *literally* and mis-set your project. Export it in your own shell instead —
  the client passes the ambient environment through:
  ```bash
  export CLOUDSDK_CORE_PROJECT=your-project-id
  gcloud auth application-default login
  ```
- **The capability table below lists logical GCP capabilities**, not entries in
  `mcp.json`. Most are reachable through the `gcloud` server; anything needing
  its own config file is an opt-in you add to your client's own MCP settings.

## Developer Knowledge — shipped in the harness manifests

`developer-knowledge` is Google's remote MCP server for official documentation
(Google Cloud, Firebase, Android, Web, Gemini), at
`developerknowledge.googleapis.com/mcp` over streamable HTTP. Use it for
platform facts — GA status, quotas, which role or service — before relying on
memory. For `gcloud` flag syntax, `gcloud help` stays the authority
(see `gcloud-guardrails`).

| Harness | Manifest | Auth |
|---------|----------|------|
| Claude Code | `.mcp.json` | API key in `DEVELOPERKNOWLEDGE_API_KEY`, sent as `X-Goog-Api-Key` |
| Antigravity | `mcp_config.json` | ADC (`authProviderType: google_credentials`) — no key |
| Gemini CLI | `gemini-extension.json` | ADC (`authProviderType: google_credentials`) — no key |

It is **not** in the portable `mcp.json`: it needs either a key or client-managed
ADC, and Agent Plugins 1.0.0 expands neither. For Claude Code:

```bash
# Create a key restricted to the Developer Knowledge API, then:
export DEVELOPERKNOWLEDGE_API_KEY=...   # in your shell profile, never in a repo
```

If the variable is unset, the server is configured with an empty key and its
calls fail authentication; the rest of the plugin is unaffected.

## Google-Managed MCP Servers (v0.1)

| Server | Capability | Required Role |
|--------|-----------|---------------|
| `google-cloud-run` | Deploy/manage Cloud Run services | `roles/run.admin` |
| `google-bigquery` | Query/manage BigQuery datasets | `roles/bigquery.user` |
| `google-gke` | GKE cluster management | `roles/container.developer` |
| `google-storage` | Cloud Storage bucket ops | `roles/storage.objectAdmin` |
| `google-vertex-ai` | Vertex AI model/endpoint management | `roles/aiplatform.user` |
| `google-iam` | IAM policy management | `roles/iam.securityAdmin` |
| `google-logging` | Cloud Logging query/ingest | `roles/logging.viewer` |
| `google-monitoring` | Metrics, alerting | `roles/monitoring.viewer` |

## GenAI Toolbox (Google's MCP for Databases) — opt-in

Google's MCP Toolbox for Databases enables LLM agents to query Cloud SQL, AlloyDB, Spanner, BigQuery, and more safely.

> **Why this is not in `mcp.json`.** Toolbox needs `--config <your tools.yaml>`,
> a path only you can supply. No Agent Plugins placeholder can express it, so
> shipping it in the portable manifest would mean a server that fails to start
> on every fresh install. Add it to your own client config once you have a
> `tools.yaml`. (A failing server is isolated by spec — it would not take the
> skills down — but a broken default is still a broken default.)

```bash
# Run the toolbox MCP server (requires a tools.yaml pointing at your database)
# Tested 2026-07-23: this is the correct package. Full docs: https://mcp-toolbox.dev
npx -y @toolbox-sdk/server --stdio --config tools.yaml

# Example tools.yaml (BigQuery source)
# sources:
#   my-bq:
#     kind: bigquery
#     project: PROJECT_ID
# tools:
#   run_query:
#     source: my-bq
#     description: Run a read-only BigQuery query
#     statement: SELECT ...
```

> **Package note (tested 2026-07-23):** use `@toolbox-sdk/server` via npx — **not** `pip install toolbox-core` / `uvx toolbox-core`. `toolbox-core` is the Python SDK *library* for building apps; it has no server CLI entry point.

- [MCP Toolbox for Databases (announcement)](https://cloud.google.com/blog/products/ai-machine-learning/mcp-toolbox-for-databases-now-supports-model-context-protocol)
- [GitHub: googleapis/genai-toolbox](https://github.com/googleapis/genai-toolbox)

## Self-Hosted / Community MCPs

| Server | Install | Use |
|--------|---------|-----|
| `gcloud-mcp` | `npx @modelcontextprotocol/server-gcloud` | Broad gcloud CLI coverage |
| `k8s-mcp` | Standard k8s MCP server | Kubernetes API for GKE |

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `401 Unauthorized` | ADC not set or expired | `gcloud auth application-default login` |
| `403 Permission Denied` | SA missing required role | Add role per table above |
| `MCP server not found` | Server not installed | Check install step in references/ |
| Connection timeout | VPC firewall blocking | Verify Private Google Access + firewall |
| `developer-knowledge` returns `401`/`403` | Key unset, or API not enabled on the quota project | Export `DEVELOPERKNOWLEDGE_API_KEY`; enable the Developer Knowledge API |

## References

- [GenAI Toolbox Docs](https://github.com/googleapis/genai-toolbox/blob/main/README.md)
- [Model Context Protocol Spec](https://modelcontextprotocol.io/introduction)
- [MCP Servers Registry](https://github.com/modelcontextprotocol/servers)
