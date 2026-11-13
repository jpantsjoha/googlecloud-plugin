#!/usr/bin/env python3
"""Print request headers for the Developer Knowledge MCP server from local ADC.

Claude Code runs this as the server's `headersHelper` (from the plugin root) on
every connection and after a 401/403. It prints a JSON object of headers:

- `Authorization: Bearer <token>` from `gcloud auth application-default
  print-access-token`.
- `X-Goog-User-Project: <project>`: user ADC is rejected (403) without a quota
  project. Taken from the ADC file's `quota_project_id`, else the gcloud
  project.

On any failure (no gcloud, not logged in, timeout) it prints `{}` and exits 0,
so the static `X-Goog-Api-Key` header in .mcp.json still applies. Nothing is
written to disk and the token never reaches stderr.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

TIMEOUT = 4  # seconds per gcloud call; Claude Code gives the helper 10 in total


def gcloud(*args: str) -> str:
    exe = shutil.which("gcloud")
    if not exe:
        return ""
    try:
        out = subprocess.run([exe, *args], capture_output=True, text=True, timeout=TIMEOUT)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return out.stdout.strip() if out.returncode == 0 else ""


def adc_quota_project() -> str:
    config = os.environ.get("CLOUDSDK_CONFIG") or str(Path.home() / ".config" / "gcloud")
    try:
        data = json.loads((Path(config) / "application_default_credentials.json").read_text())
    except (OSError, ValueError):
        return ""
    value = data.get("quota_project_id") if isinstance(data, dict) else None
    return value if isinstance(value, str) else ""


def headers() -> dict[str, str]:
    token = gcloud("auth", "application-default", "print-access-token")
    if not token:
        return {}
    result = {"Authorization": f"Bearer {token}"}
    project = adc_quota_project() or gcloud("config", "get-value", "project")
    if project and project != "(unset)":
        result["X-Goog-User-Project"] = project
    return result


if __name__ == "__main__":
    json.dump(headers(), sys.stdout)
