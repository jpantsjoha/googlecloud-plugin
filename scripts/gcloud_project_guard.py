#!/usr/bin/env python3
"""PreToolUse guard: no project-scoped gcloud call runs without an explicit --project.

Claude Code runs this before the plugin's `run_gcloud_command` MCP tool and
before Bash commands. When a project-scoped gcloud command lacks --project, it
blocks the call and tells the agent what the project sources say (see
gcp-project-context): one project → retry with it; several → ask the user;
none → ask the user or suggest `gcloud init`. Everything else passes untouched.

Reads the hook event as JSON on stdin. Never prints .env contents beyond the
project IDs the resolver already validates.
"""
import json
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import preflight  # noqa: E402  (sibling script, shared resolver)

MCP_TOOL_SUFFIX = "__run_gcloud_command"
# Command groups that are not project-scoped, or take the project positionally.
EXEMPT_GROUPS = {"auth", "components", "config", "help", "info", "init", "meta", "topic", "version",
                 "projects", "organizations", "billing"}
PROJECT_FLAGS = ("--project", "--billing-project")


def gcloud_argv(tool_name: str, tool_input: dict) -> list[str] | None:
    """The gcloud arguments (without 'gcloud') this call would run, or None if it is not a gcloud call."""
    if tool_name.endswith(MCP_TOOL_SUFFIX):
        if isinstance(tool_input.get("args"), list):
            return [str(a) for a in tool_input["args"]]
        command = tool_input.get("command")
    elif tool_name == "Bash":
        command = tool_input.get("command")
    else:
        return None
    if not isinstance(command, str):
        return None
    try:
        tokens = shlex.split(command)
    except ValueError:
        return None
    # Bash: only a command that starts with gcloud (optionally after env assignments).
    while tokens and "=" in tokens[0] and not tokens[0].startswith("-"):
        tokens = tokens[1:]
    if tokens and tokens[0] == "env":
        tokens = tokens[1:]
        while tokens and ("=" in tokens[0] or tokens[0] in ("-u", "-i")):
            tokens = tokens[2:] if tokens[0] == "-u" else tokens[1:]
    if not tokens or Path(tokens[0]).name != "gcloud":
        return None if tool_name == "Bash" else tokens
    return tokens[1:]


def needs_project(argv: list[str]) -> bool:
    if any(a == f or a.startswith(f + "=") for a in argv for f in PROJECT_FLAGS):
        return False
    groups = [a for a in argv if not a.startswith("-")]
    while groups and groups[0] in ("alpha", "beta"):
        groups = groups[1:]
    return bool(groups) and groups[0] not in EXEMPT_GROUPS


def guidance(cwd: Path) -> str:
    candidates = preflight.collect_project_candidates(cwd)
    result = preflight.resolve_project(candidates)
    by_value: dict[str, list[str]] = {}
    for c in candidates:
        if c["valid"]:
            by_value.setdefault(c["value"], []).append(c["source"])
    lines = ["Blocked: this gcloud command is project-scoped and has no --project (gcp-project-context)."]
    if result["status"] == "resolved":
        sources = ", ".join(by_value[result["project"]])
        lines.append(f"One project found: {result['project']} (from {sources}). "
                     f"Tell the user you are using it, then re-run with --project={result['project']}.")
    elif result["status"] == "conflict":
        lines.append("Project sources disagree. Ask the user which project to use before running anything:")
        lines += [f"  - {value}  ({', '.join(srcs)})" for value, srcs in by_value.items()]
        if result["gcloud_uses"]:
            lines.append(f"gcloud alone would use {result['gcloud_uses']}.")
        lines.append("Then re-run with --project=<their choice>.")
    else:
        lines.append("No project is configured in the environment, .env/.env.local or gcloud config. "
                     "Ask the user for the project ID, or suggest `gcloud init` or "
                     "`gcloud config set project PROJECT_ID`.")
    for c in result["invalid"]:
        lines.append(f"Note: {c['source']} holds an invalid project value; report it to the user.")
    return "\n".join(lines)


def decide(event: dict) -> str | None:
    """Reason to block, or None to allow."""
    argv = gcloud_argv(str(event.get("tool_name", "")), event.get("tool_input") or {})
    if argv is None or not needs_project(argv):
        return None
    return guidance(Path(event.get("cwd") or Path.cwd()))


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except (ValueError, OSError):
        return  # not our input; never block on a parse failure
    reason = decide(event)
    if reason:
        print(reason, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
