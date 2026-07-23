# Research Sources

Last updated: 2026-07-23 (scaffold — populated by `make crawl`)

Every source URL is stored with retrieval date and content hash for audit.
Run `make crawl` to populate this file with live hashes.

This file is the authoritative audit trail: every claim in every skill traces to a URL here.

---

## How to read this file

Each entry has:
- **URL** — the canonical source
- **Retrieved** — ISO 8601 timestamp of last crawl
- **Hash** — SHA256 of response body at retrieval time
- **Status** — HTTP status at last crawl

Run `make check` to detect drift between stored hashes and live sources.

---

*Run `make crawl` to populate entries below.*
