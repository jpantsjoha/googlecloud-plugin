# Shared Auth Patterns

All skills in this plugin authenticate via one of three patterns. No credential values are ever stored — paths only.

## Bootstrap: infer from the environment, prompt only if missing

The plugin does **not** ship an `init` that logs you in or hardcodes a project. It infers your GCP context from the environment and proceeds — especially for read-only work — and prompts for a login only when context is genuinely absent. Run:

```bash
make preflight     # read-only; detects project + credentials, never logs in
```

**Project precedence:** `GOOGLE_CLOUD_PROJECT` → `GCP_PROJECT_ID` → `CLOUDSDK_CORE_PROJECT` → `gcloud config get-value project` → prompt.

**Credential precedence:** `GOOGLE_APPLICATION_CREDENTIALS` (path) → ADC file (`~/.config/gcloud/application_default_credentials.json`) → active `gcloud` account → prompt.

If context is present, skills proceed. If missing, `preflight` prints the exact command (`gcloud auth application-default login`, `gcloud config set project …`) — it never installs the SDK for you (system-level) and never stores a credential value.

**Read-only vs mutation:** read-only discovery may proceed on inferred context; any billable or mutating action still warns and confirms per the gate, and stops if credentials are absent.

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
