---
name: mcp-servers
description: "Configure, install, and maintain Google-managed and self-hosted MCP servers for GCP. Covers setup, auth (ADC and SA key), capability map, troubleshooting, and version tracking. Every MCP entry includes a gcloud CLI fallback."
version: "0.1"
triggers:
  - "MCP server"
  - "MCP setup"
  - "google MCP"
  - "model context protocol GCP"
  - "MCP install"
  - "MCP auth"
  - "genai toolbox"
  - "MCP tools GCP"
  - "configure MCP"
required_scopes: []
mcp_servers:
  - google-cloud-run
  - google-bigquery
  - google-gke
  - google-storage
  - google-vertex-ai
  - google-iam
  - google-logging
  - google-monitoring
---

# MCP Servers — Google Cloud

Configure and maintain Model Context Protocol (MCP) servers for Google Cloud. All auth flows through ADC or explicit SA key path — no credential values stored anywhere.

## Auth Architecture

All GCP MCP servers authenticate via Application Default Credentials (ADC):

```bash
# Authenticate locally (developer machine)
gcloud auth application-default login

# Authenticate for a service account (CI/CD or production agent)
gcloud auth activate-service-account --key-file=/path/to/sa-key.json
gcloud auth application-default login --impersonate-service-account=SA@PROJECT.iam.gserviceaccount.com
```

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

## GenAI Toolbox (Google's MCP for Databases)

Google's MCP Toolbox for Databases enables LLM agents to query Cloud SQL, AlloyDB, Spanner, BigQuery, and more safely.

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

## References

- [GenAI Toolbox Docs](https://github.com/googleapis/genai-toolbox/blob/main/README.md)
- [Model Context Protocol Spec](https://modelcontextprotocol.io/introduction)
- [MCP Servers Registry](https://github.com/modelcontextprotocol/servers)
