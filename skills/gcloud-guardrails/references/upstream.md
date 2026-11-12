# Provenance

The four-step plan, the execution rules and the denylist adapt the `gcloud` skill (v1.0.3) in Google's `google-cloud-developer` plugin (v1.1.17), published in the `google/skills` repository under the Apache License 2.0. See `NOTICE` at the repository root.

Differences from upstream:

- Rewritten in this plugin's voice and tied to ADR-004 and the security gate.
- IAM changes route through the `iam` skill.
- `--quiet` is ordered after the denylist check, because it accepts destructive prompts.
- Usage-attribution environment variables and headers are omitted; they report usage to Google.

Upstream source: https://github.com/google/skills/tree/main/plugins/cloud/google-cloud-developer
