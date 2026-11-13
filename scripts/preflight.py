#!/usr/bin/env python3
"""Preflight: infer GCP context from the environment; prompt only if missing.

Read-only and non-mutating. It NEVER logs in, stores, or prints a credential
value — it detects what is already available and, if something is missing,
tells the user the exact command to run.

Project resolution collects every candidate rather than stopping at the first:
environment variables, the project's .env files, and the active gcloud
configuration. One distinct value means the project is resolved. Two or more
is a conflict the user must settle — common when several projects share a
machine — so this script reports each source and never picks for them.

Usage:
    python3 scripts/preflight.py [--project-dir DIR] [--json]

Exit 0: enough context to proceed (one project + credentials inferable).
Exit 2: context missing — guidance printed.
Exit 3: project sources disagree — the user picks one.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

# Environment variables that name a project, in the order Google tooling reads
# them. gcloud itself honours only CLOUDSDK_CORE_PROJECT (over its active
# configuration); the others are read by client libraries, Terraform and apps.
PROJECT_ENV_VARS = ["CLOUDSDK_CORE_PROJECT", "GOOGLE_CLOUD_PROJECT", "GCP_PROJECT_ID", "GCLOUD_PROJECT"]
# Project-level files checked for the same keys. Only these keys are read;
# nothing else in the file is parsed, stored or printed.
DOTENV_FILES = [".env", ".env.local"]
ADC_DEFAULT = Path.home() / ".config" / "gcloud" / "application_default_credentials.json"
# A valid project ID: 6-30 chars, lowercase letters, digits, hyphens, starting
# with a letter. Anything else (an unexpanded "${VAR}", "(unset)", a typo) is
# reported as invalid instead of being treated as a candidate.
PROJECT_ID = re.compile(r"^[a-z][a-z0-9-]{4,28}[a-z0-9]$")
DOTENV_LINE = re.compile(r"^\s*(?:export\s+)?([A-Z_][A-Z0-9_]*)\s*=\s*(.*?)\s*$")


def _run(cmd: list[str]) -> str | None:
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        val = out.stdout.strip()
        return val or None
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        return None


def _dotenv_projects(path: Path) -> list[tuple[str, str]]:
    """Return (key, value) for project keys in one dotenv file; other keys are skipped unread."""
    try:
        lines = path.read_text(errors="replace").splitlines()
    except OSError:
        return []
    found = []
    for line in lines:
        match = DOTENV_LINE.match(line)
        if not match or match.group(1) not in PROJECT_ENV_VARS:
            continue
        value = match.group(2).split(" #", 1)[0].strip().strip("'\"")
        found.append((match.group(1), value))
    return found


def collect_project_candidates(project_dir: Path, env: dict[str, str] | None = None) -> list[dict]:
    """Every place a project is named, in precedence order, each with its source."""
    env = os.environ if env is None else env
    candidates: list[dict] = []
    for var in PROJECT_ENV_VARS:
        if env.get(var):
            candidates.append({"source": f"env:{var}", "value": env[var]})
    for name in DOTENV_FILES:
        for key, value in _dotenv_projects(project_dir / name):
            if value:
                candidates.append({"source": f"{name}:{key}", "value": value})
    if shutil.which("gcloud"):
        configuration = _run(["gcloud", "config", "configurations", "list",
                              "--filter=is_active=true", "--format=value(name)"])
        proj = _run(["gcloud", "config", "get-value", "project"])
        if proj and proj != "(unset)":
            label = f"gcloud config ({configuration})" if configuration else "gcloud config"
            # With CLOUDSDK_CORE_PROJECT set, get-value echoes it; only count the
            # configuration when it is a distinct source.
            if proj != env.get("CLOUDSDK_CORE_PROJECT"):
                candidates.append({"source": label, "value": proj})
    for c in candidates:
        c["valid"] = bool(PROJECT_ID.match(c["value"]))
    return candidates


def resolve_project(candidates: list[dict]) -> dict:
    """resolved: one distinct valid value. conflict: several. missing: none."""
    valid = [c for c in candidates if c["valid"]]
    distinct = list(dict.fromkeys(c["value"] for c in valid))
    gcloud_uses = next((c["value"] for c in valid
                        if c["source"] == "env:CLOUDSDK_CORE_PROJECT" or c["source"].startswith("gcloud config")), None)
    if not distinct:
        status = "missing"
    elif len(distinct) == 1:
        status = "resolved"
    else:
        status = "conflict"
    return {
        "status": status,
        "project": distinct[0] if status == "resolved" else None,
        "choices": distinct,
        "gcloud_uses": gcloud_uses,
        "invalid": [c for c in candidates if not c["valid"]],
    }


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


PROJECT_GUIDANCE = {
    "missing": (
        "No project found. Run `gcloud init`, or set one:\n"
        "        gcloud config set project PROJECT_ID          # this machine's default\n"
        "        echo 'GOOGLE_CLOUD_PROJECT=PROJECT_ID' >> .env  # this repository"
    ),
    "conflict": (
        "Project sources disagree. Pick one, then keep them consistent:\n"
        "        gcloud config configurations create NAME   # one named configuration per project\n"
        "        gcloud config set project PROJECT_ID\n"
        "        # or align .env / exported variables to the same ID\n"
        "      Until then, pass --project=PROJECT_ID on every command."
    ),
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--project-dir", type=Path, default=Path.cwd(),
                        help="repository whose .env files to read (default: current directory)")
    parser.add_argument("--json", action="store_true", help="print the project resolution as JSON")
    args = parser.parse_args()

    candidates = collect_project_candidates(args.project_dir)
    project = resolve_project(candidates)
    have_creds, csrc = detect_credentials()

    if args.json:
        print(json.dumps({"project": project, "candidates": candidates,
                          "credentials": {"present": have_creds, "source": csrc}}, indent=2))
    else:
        print("==> GoogleCloud Plugin preflight (read-only; infers context, never logs in)\n")
        if shutil.which("gcloud"):
            ver = _run(["gcloud", "version"]) or ""
            print(f"OK    gcloud SDK       : {ver.splitlines()[0] if ver else 'installed'}")
        else:
            print("WARN  gcloud SDK       : not on PATH — install from "
                  "https://cloud.google.com/sdk/docs/install (the plugin will not install it)")

        for c in candidates:
            mark = "    " if c["valid"] else "BAD "
            print(f"{mark}  project source   : {c['value']:30s} ({c['source']})")
        for c in project["invalid"]:
            print(f"WARN  invalid project  : {c['value']!r} from {c['source']} is not a project ID")
        if project["status"] == "resolved":
            print(f"OK    GCP project      : {project['project']}")
        elif project["status"] == "conflict":
            print(f"WARN  GCP project      : sources disagree — {', '.join(project['choices'])}")
            if project["gcloud_uses"]:
                print(f"      gcloud would use : {project['gcloud_uses']}")
        else:
            print("WARN  GCP project      : not set")

        print(f"{'OK  ' if have_creds else 'WARN'}  credentials      : "
              f"{'present  (via ' + csrc + ')' if have_creds else 'none found — run: gcloud auth application-default login'}")
        print(f"{'OK  ' if shutil.which('npx') else 'note'}  npx              : "
              f"{'available' if shutil.which('npx') else 'absent (only needed for the gcloud MCP server)'}")
        print()
        if project["status"] in PROJECT_GUIDANCE:
            print(PROJECT_GUIDANCE[project["status"]])
        elif have_creds:
            print("Ready: project and credentials inferred from your environment.")
            print("Read-only discovery is safe; mutations still warn and confirm per the gate.")

    if project["status"] == "conflict":
        raise SystemExit(3)
    if project["status"] == "missing" or not have_creds:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
