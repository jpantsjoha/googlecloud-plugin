#!/usr/bin/env python3
"""Compare stored content hashes against live sources and report drift.

Reads research/SOURCES.md for stored hashes, re-fetches each URL,
and flags any mismatch. Updates the local hash cache.

Exit 0: all sources fresh (or no stored hashes to compare).
Exit 1: one or more sources have drifted.
"""
import sys
import json
import hashlib
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).parent.parent
CACHE_FILE = ROOT / "research" / ".hash-cache.json"
SOURCES_FILE = ROOT / "research" / "SOURCES.md"
TIMEOUT = 20
HEADERS = {"User-Agent": "googlecloud-plugin/0.1 freshness-checker"}


def fetch_hash(url: str) -> tuple[str, str]:
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            content = r.read()
            return hashlib.sha256(content).hexdigest(), "OK"
    except urllib.error.HTTPError as e:
        return "", f"HTTP {e.code}"
    except Exception as e:
        return "", f"{type(e).__name__}: {e}"


def parse_sources() -> list[dict]:
    if not SOURCES_FILE.exists():
        return []
    sources: list[dict] = []
    current: dict = {}
    for line in SOURCES_FILE.read_text().splitlines():
        if line.startswith("### "):
            if current.get("url"):
                sources.append(current)
            current = {"title": line.lstrip("# ").strip()}
        elif line.startswith("- **URL**:"):
            current["url"] = line.split(":", 1)[1].strip()
        elif line.startswith("- **Hash**:"):
            current["stored_hash"] = line.split(":", 1)[1].strip()
        elif line.startswith("- **Retrieved**:"):
            current["retrieved"] = line.split(":", 1)[1].strip()
    if current.get("url"):
        sources.append(current)
    return sources


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def main():
    sources = parse_sources()
    if not sources:
        print("No sources found in research/SOURCES.md — nothing to check")
        sys.exit(0)

    cache: dict = {}
    if CACHE_FILE.exists():
        try:
            cache = json.loads(CACHE_FILE.read_text())
        except json.JSONDecodeError:
            cache = {}

    drifted: list[str] = []
    errors: list[str] = []
    fresh = 0

    for s in sources:
        url = s.get("url", "").strip()
        if not url or not url.startswith("http"):
            continue

        stored = s.get("stored_hash", "").strip()
        live_hash, status = fetch_hash(url)

        if status != "OK":
            print(f"ERR   {url}")
            print(f"      {status}")
            errors.append(url)
            continue

        cache[url] = {"hash": live_hash, "checked": now_iso()}

        if not stored:
            print(f"NEW   {url}")
            print(f"      No stored hash — recorded {live_hash[:16]}...")
        elif live_hash != stored:
            print(f"DRIFT {url}")
            print(f"      stored: {stored[:16]}...")
            print(f"      live:   {live_hash[:16]}...")
            drifted.append(url)
        else:
            print(f"OK    {url}")
            fresh += 1

    CACHE_FILE.write_text(json.dumps(cache, indent=2))

    print()
    summary = f"{fresh} fresh, {len(drifted)} drifted, {len(errors)} error(s)"
    print(summary)

    if drifted:
        print(f"\nAction required: {len(drifted)} source(s) changed — update affected skills")
        sys.exit(1)


if __name__ == "__main__":
    main()
