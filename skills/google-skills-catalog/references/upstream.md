# Provenance

The fetch, verify, shortlist and failure workflow adapts the `finding-google-skills` skill (v1.1.0) and the `google-cloud-discovery.md` routing rule in Google's `google-cloud-developer` plugin (v1.1.17), published in the `google/skills` repository under the Apache License 2.0. See `NOTICE` at the repository root.

Differences from upstream:

- Positioned as the product-depth layer beneath this plugin's personas and delivery gate; gate rules win on conflict.
- Windows PowerShell variants omitted.

Upstream source: https://github.com/google/skills/tree/main/plugins/cloud/google-cloud-developer
