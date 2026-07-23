# ADR-002: Content Hash + URL Audit Trail

**Status:** Accepted  
**Date:** 2026-07-23

## Context

GCP documentation evolves rapidly. Skills that reference stale docs mislead developers. Manual tracking fails at scale. Compliance and vendor audits require traceability ("which docs informed this skill?").

## Decision

Every reference doc is stored with:
- Source URL
- Retrieval date (ISO 8601)
- SHA256 hash of the response body
- Last-modified header (if present)

`freshness_check.py` re-fetches weekly and flags any hash mismatch. Stored in `research/SOURCES.md`. Local hash cache in `research/.hash-cache.json` (gitignored).

## Consequences

- ✅ Drift detected automatically — no silent staleness
- ✅ Full audit trail: every skill reference traces to a dated, hashed source
- ✅ Weekly CI trigger keeps the plugin current without manual effort
- ⚠️ ~1 sec per URL fetch; 50 docs = ~5 min crawl (acceptable for weekly schedule)
- ⚠️ Redirects (301/302) must be followed; final URL hashed, redirect chain logged
