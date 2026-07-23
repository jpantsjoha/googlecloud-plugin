# Shared Auth Patterns

All skills in this plugin authenticate via one of three patterns. No credential values are ever stored — paths only.

## Pattern 1 — Application Default Credentials (ADC) — Preferred

```bash
# Developer machine
gcloud auth application-default login

# Verify what ADC is currently set to
gcloud auth application-default print-access-token

# CI/CD — impersonate a SA (no key file needed)
gcloud auth application-default login \
  --impersonate-service-account=SA_EMAIL@PROJECT.iam.gserviceaccount.com
```

ADC is the default for all SDK calls and most GCP client libraries. Use this first.

## Pattern 2 — Service Account Key File (use only when ADC is not possible)

```bash
# Activate a SA key file
gcloud auth activate-service-account --key-file=/path/to/sa-key.json

# Set for ADC
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/sa-key.json
```

Prefer Workload Identity over key files wherever the runtime supports it (GKE, Cloud Run, GCE).

## Pattern 3 — Workload Identity (GKE workloads)

See `skills/gke/SKILL.md` and `skills/iam/SKILL.md` for the full Workload Identity binding pattern.

## MCP Auth

All GCP MCP servers consume ADC automatically when `GOOGLE_APPLICATION_CREDENTIALS` is set or `gcloud auth application-default login` has been run.

See `skills/mcp-servers/SKILL.md` for per-server required roles.

## Never Do

- Store a SA key file value (JSON content) in any skill, script, or reference doc
- Commit `.json` key files to git
- Use `roles/owner` or `roles/editor` for service account bindings
- Share SA key files across environments
