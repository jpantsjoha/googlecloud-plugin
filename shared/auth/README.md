# Shared Auth Patterns

All skills in this plugin authenticate via one of four patterns, in order of preference. None needs a downloaded service-account key. No credential values are ever stored.

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

```

ADC is the default for all SDK calls and most GCP client libraries. Use this first.

## Pattern 2 — Service-account impersonation (act as a service account without its key)

Your own identity mints short-lived tokens for the service account. Nothing is downloaded, and every call is audited under both identities.

```bash
# One command
gcloud run services list --project=PROJECT_ID --limit=20 \
  --impersonate-service-account=SA_NAME@PROJECT_ID.iam.gserviceaccount.com

# Every gcloud command in this configuration
gcloud config set auth/impersonate_service_account SA_NAME@PROJECT_ID.iam.gserviceaccount.com

# Client libraries and MCP servers (ADC)
gcloud auth application-default login \
  --impersonate-service-account=SA_NAME@PROJECT_ID.iam.gserviceaccount.com
```

Prerequisite: your identity needs `roles/iam.serviceAccountTokenCreator` **on that service account** (not on the project). Granting it is an IAM change — a named human authorises it through the `iam` skill.

## Pattern 3 — Attached service accounts and Workload Identity (code running on Google Cloud)

Cloud Run, Compute Engine and Cloud Functions take an attached service account; the runtime supplies tokens and ADC finds them. GKE pods use Workload Identity Federation for GKE. See `skills/gke/SKILL.md` and `skills/iam/SKILL.md` for the binding pattern.

## Pattern 4 — Workload Identity Federation (CI and other clouds)

GitHub, GitLab, AWS and Azure workloads exchange their own identity token for a short-lived Google token. The configuration file this produces holds **no secret** — it says where to read the external token and which service account to impersonate.

Prerequisites, each an IAM or trust change a named human authorises:

1. A workload identity pool and provider for the external issuer, with an **attribute condition** that pins the exact workload (for GitHub: the repository, and ideally the branch or environment). Trusting the issuer alone admits every workload that issuer serves.
2. `roles/iam.workloadIdentityUser` **on the target service account**, granted to the narrowest principal set the mapping allows (for example `principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/attribute.repository/OWNER/REPO`) — never to the whole pool. This flow does not use `roles/iam.serviceAccountTokenCreator`.
3. The service account itself holds only the roles the workload needs on its target resources.

Example for a workload whose OIDC token is written to a file:

```bash
gcloud iam workload-identity-pools create-cred-config \
  projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/providers/PROVIDER_ID \
  --service-account=SA_NAME@PROJECT_ID.iam.gserviceaccount.com \
  --credential-source-file=PATH_TO_OIDC_TOKEN \
  --output-file=wif-credentials.json

export GOOGLE_APPLICATION_CREDENTIALS=wif-credentials.json   # ADC now uses federation
```

Other environments swap the source flag: `--credential-source-url` (token served over HTTP, with `--credential-source-headers` if needed), `--aws`, or `--azure`. Validate the exact form with `gcloud help iam workload-identity-pools create-cred-config`.

## Service-account keys — exception only

A downloaded JSON key is a long-lived bearer credential: anyone who copies it is that service account until someone notices and deletes it. Many organisations block key creation with the `iam.disableServiceAccountKeyCreation` org policy.

Use one only when none of the patterns above can work (for example a third-party system that accepts nothing else). Then:

- A named human creates it; agents never do (`iam service-accounts keys create` is on the `gcloud-guardrails` denylist).
- Record the reason, owner and expiry in the design; reference the key by path, never by value.
- Rotate it, and delete it when the exception ends.

## MCP Auth

All GCP MCP servers consume ADC automatically after `gcloud auth application-default login` (with `--impersonate-service-account` to act as a service account), or from a Workload Identity Federation file named in `GOOGLE_APPLICATION_CREDENTIALS`.

See `skills/mcp-servers/SKILL.md` for per-server required roles.

## Never Do

- Store a SA key file value (JSON content) in any skill, script, or reference doc
- Commit `.json` key files to git
- Use `roles/owner` or `roles/editor` for service account bindings
- Share SA key files across environments
- Create, download or activate a service-account key on an agent's own initiative
