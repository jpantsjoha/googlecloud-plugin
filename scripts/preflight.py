#!/usr/bin/env python3
"""Preflight: infer GCP context from the environment; prompt only if missing.

Read-only and non-mutating. It NEVER logs in, stores, or prints a credential
value — it detects what is already available and, if something is missing,
tells the user the exact command to run.

Design (per plugin UX): infer from the environment and proceed — especially for
read-only work — and fall back to a login prompt only when context is absent.

Exit 0: enough context to proceed (project + credentials inferable).
Exit 2: context missing — guidance printed. (Non-fatal: callers may still allow
        read-only discovery, but mutations should stop until resolved.)
"""
import os
import shutil
import subprocess
from pathlib import Path

# Precedence order matches Google's own tooling conventions.
PROJECT_ENV_VARS = ["GOOGLE_CLOUD_PROJECT", "GCP_PROJECT_ID", "CLOUDSDK_CORE_PROJECT"]
ADC_DEFAULT = Path.home() / ".config" / "gcloud" / "application_default_credentials.json"


def _run(cmd: list[str]) -> str | None:
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        val = out.stdout.strip()
        return val or None
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        return None


def detect_project() -> tuple[str | None, str]:
    for var in PROJECT_ENV_VARS:
        if os.environ.get(var):
            return os.environ[var], f"env:{var}"
    if shutil.which("gcloud"):
        proj = _run(["gcloud", "config", "get-value", "project"])
        if proj and proj != "(unset)":
            return proj, "gcloud config"
    return None, "not found"


def detect_credentials() -> tuple[bool, str]:
    explicit = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if explicit and Path(explicit).exists():
        return True, "env:GOOGLE_APPLICATION_CREDENTIALS (path)"
    if ADC_DEFAULT.exists():
        return True, "ADC (application_default_credentials.json)"
    if shutil.which("gcloud"):
        acct = _run(["gcloud", "config", "get-value", "account"])
        if acct and acct != "(unset)":
            return True, f"gcloud active account ({acct})"
    return False, "not found"


def main() -> None:
    print("==> GoogleCloud Plugin preflight (read-only; infers context, never logs in)\n")

    ready = True
    prompts: list[str] = []

    # gcloud SDK — detect only; never auto-install system software.
    if shutil.which("gcloud"):
        ver = _run(["gcloud", "version"]) or ""
        first = ver.splitlines()[0] if ver else "installed"
        print(f"OK    gcloud SDK        : {first}")
    else:
        print("WARN  gcloud SDK        : not on PATH")
        prompts.append(
            "Install the gcloud SDK: https://cloud.google.com/sdk/docs/install "
            "(system-level — the plugin will not install it for you)"
        )
        ready = False

    # Project — inferred from env, else gcloud config, else prompt.
    project, src = detect_project()
    if project:
        print(f"OK    GCP project      : {project}  (via {src})")
    else:
        print("WARN  GCP project      : not set")
        prompts.append(
            "Set a project (either works):\n"
            "        export GOOGLE_CLOUD_PROJECT=your-project-id\n"
            "        gcloud config set project your-project-id"
        )
        ready = False

    # Credentials — ADC preferred; prompt to login if absent. No values printed.
    have_creds, csrc = detect_credentials()
    if have_creds:
        print(f"OK    credentials      : present  (via {csrc})")
    else:
        print("WARN  credentials      : none found")
        prompts.append(
            "Authenticate (Application Default Credentials):\n"
            "        gcloud auth application-default login"
        )
        ready = False

    # MCP runtimes — needed only if using the MCP servers (.mcp.json).
    for tool, why in (("npx", "gcloud MCP server"), ("uvx", "GenAI Toolbox MCP")):
        mark = "OK  " if shutil.which(tool) else "note"
        state = "available" if shutil.which(tool) else "absent (only needed for MCP)"
        print(f"{mark}  {tool:16s}: {state}  [{why}]")

    print()
    if ready:
        print("Ready: project + credentials inferred from your environment. Proceeding.")
        print("Read-only discovery is safe; mutations still warn + confirm per the gate.")
        return

    print("Some context is missing. For read-only exploration the plugin can still")
    print("proceed where possible, but resolve these before any mutation:\n")
    for i, p in enumerate(prompts, 1):
        print(f"  {i}. {p}")
    raise SystemExit(2)


if __name__ == "__main__":
    main()
