#!/usr/bin/env python3
"""Print request headers for the Developer Knowledge MCP server from local ADC.

Claude Code runs this as the server's `headersHelper` (from the plugin root) on
every connection and after a 401/403. It prints a JSON object of headers:

- `Authorization: Bearer <token>` from `gcloud auth application-default
  print-access-token`.
- `X-Goog-User-Project: <project>`: user ADC is rejected (403) without a quota
  project. Taken from the ADC file's `quota_project_id`, else the gcloud
  project.

Both headers or neither: a token without a quota project is refused, and an
Authorization header would also stop Claude Code falling back. So on any
failure (no gcloud, not logged in, no quota project, a lookup timing out) it
prints `{}` and exits 0, and the static `X-Goog-Api-Key` header in .mcp.json
applies instead. Nothing is
written to disk and the token never reaches stderr.
"""
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

BUDGET = 8.0  # seconds for the whole helper; Claude Code gives up at 10


def gcloud(deadline: float, *args: str) -> str:
    exe = shutil.which("gcloud")
    remaining = deadline - time.monotonic()
    if not exe or remaining <= 0.5:
        return ""
    try:
        out = subprocess.run([exe, *args], capture_output=True, text=True, timeout=remaining)
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
    deadline = time.monotonic() + BUDGET
    project = adc_quota_project() or gcloud(deadline, "config", "get-value", "project")
    if not project or project == "(unset)":
        return {}
    token = gcloud(deadline, "auth", "application-default", "print-access-token")
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}", "X-Goog-User-Project": project}


if __name__ == "__main__":
    json.dump(headers(), sys.stdout)
