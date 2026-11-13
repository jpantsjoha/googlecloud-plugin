#!/usr/bin/env python3
"""PreToolUse guard: no project-scoped gcloud call runs without an explicit --project.

Claude Code runs this before the plugin's `run_gcloud_command` MCP tool and
before Bash commands. When a project-scoped gcloud invocation lacks --project,
it blocks the call (exit 2) and tells the agent what the project sources say
(see gcp-project-context): one project → retry with it; several → ask the
user; none → ask the user or suggest `gcloud init`.

Shell commands are split into individual invocations, so each gcloud call is
judged on its own flags; `sh -c` and common prefixes (sudo, env, timeout…) are
looked through. A gcloud call hidden in a command substitution cannot be
analysed and is blocked conservatively. If resolution itself fails or runs out
of time, the call is still blocked, with a generic reason.

When the project sources disagree, an explicit --project is accepted only if
the user has named that project in this session — in a message they typed or
an answer to a question (AskUserQuestion) — read from the session transcript,
which the agent cannot write. Otherwise the agent could settle the conflict
by quietly picking the gcloud default.

Reads the hook event as JSON on stdin; a malformed event is allowed through.
Requires python3 on PATH; without it Claude Code reports a hook error and the
call proceeds. Never prints .env contents beyond validated project IDs.
"""
import json
import re
import shlex
import sys
import threading
from pathlib import Path

MCP_TOOL_SUFFIX = "__run_gcloud_command"
# Command groups that are not project-scoped, or take the project positionally.
EXEMPT_GROUPS = {"auth", "components", "config", "help", "info", "init", "meta", "topic", "version",
                 "projects", "organizations", "billing"}
# gcloud-wide flags that take a value; skipped with their value when finding the command group.
VALUE_FLAGS = {"--account", "--billing-project", "--configuration", "--flags-file", "--flatten", "--format",
               "--impersonate-service-account", "--project", "--verbosity", "--access-token-file",
               "--trace-token", "--filter", "--limit", "--sort-by", "--page-size"}
HELP_FLAGS = {"--help", "-h"}
# Prefixes that run the rest of the line as a command, and their options that take a value.
WRAPPERS = {"sudo", "exec", "time", "nohup", "command", "xargs", "nice", "watch", "doas"}
WRAPPER_VALUE_OPTS = {"-u", "-g", "-U", "-C", "-D", "-h", "-p", "-r", "-t", "-T", "-n", "-I", "-L", "-P",
                      "--user", "--group", "--chdir"}
SHELLS = {"sh", "bash", "zsh", "dash", "ksh"}
SHELL_KEYWORDS = {"then", "do", "else", "elif", "if", "while", "until", "{", "}", "!", "time"}
# Commands that only print or search text: "gcloud" among their arguments is data.
TEXT_COMMANDS = {"echo", "printf", "grep", "egrep", "rg", "ag", "cat", "less", "more", "head", "tail", "man",
                 "which", "type", "whereis", "ls", "find", "sed", "awk", "wc", "sort", "uniq", "diff", "git",
                 "tee", "cut", "tr", "jq", "yq", "python3", "python", "node"}
GCLOUD_WORD = re.compile(r"(?:^|[\s;&|(/])gcloud(?:\s|$)")
MAX_DEPTH = 3
SHELL_OPERATORS = {"&&", "||", ";", "|", "&", "|&", ";;", "(", ")", "\n"}
RESOLVE_BUDGET = 8.0  # seconds; the hook timeout is 15


class Unanalysable(Exception):
    """A shell construct that may run gcloud but cannot be checked."""


def _tokens(command: str) -> list[str]:
    lexer = shlex.shlex(command.replace("\n", " ; "), posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    return list(lexer)


def _segments(tokens: list[str]) -> list[list[str]]:
    segments, current = [], []
    for tok in tokens:
        if tok in SHELL_OPERATORS or (tok and set(tok) <= set("&|;()")):
            if current:
                segments.append(current)
            current = []
        else:
            current.append(tok)
    if current:
        segments.append(current)
    return segments


def _strip_prefixes(seg: list[str]) -> list[str]:
    while seg:
        head = seg[0]
        if head in SHELL_KEYWORDS:
            seg = seg[1:]
        elif re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", head):
            seg = seg[1:]
        elif head == "env":
            seg = seg[1:]
            while seg and (seg[0].startswith("-") or "=" in seg[0]):
                seg = seg[2:] if seg[0] in ("-u", "--unset") else seg[1:]
        elif head == "timeout":
            seg = seg[1:]
            while seg and seg[0].startswith("-"):
                seg = seg[1:]
            seg = seg[1:]  # the duration
        elif Path(head).name in WRAPPERS:
            seg = seg[1:]
            while seg and seg[0].startswith("-"):
                seg = seg[2:] if (seg[0] in WRAPPER_VALUE_OPTS and len(seg) > 1) else seg[1:]
        else:
            return seg
    return seg


def shell_gcloud_invocations(command: str, depth: int = 0) -> list[list[str]]:
    """Argument lists (without 'gcloud') of every gcloud invocation in a shell command."""
    if re.search(r"\$\(|`", command) and re.search(r"\bgcloud\b", command):
        raise Unanalysable("gcloud inside a command substitution")
    try:
        tokens = _tokens(command)
    except ValueError as exc:
        if re.search(r"\bgcloud\b", command):
            raise Unanalysable("unparseable shell command containing gcloud") from exc
        return []
    found = []
    for seg in _segments(tokens):
        seg = _strip_prefixes(seg)
        if not seg:
            continue
        exe = Path(seg[0]).name
        script_idx = next((i for i, a in enumerate(seg[1:], 1)
                           if re.fullmatch(r"-[A-Za-z]*c[A-Za-z]*", a)), None) if exe in SHELLS else None
        if script_idx is not None:
            if script_idx + 1 >= len(seg):
                continue
            if depth >= MAX_DEPTH:
                raise Unanalysable("shell commands nested too deeply to check")
            found += shell_gcloud_invocations(seg[script_idx + 1], depth + 1)
        elif exe == "gcloud":
            found.append(seg[1:])
        elif exe not in TEXT_COMMANDS and any(GCLOUD_WORD.search(a) for a in seg[1:]):
            raise Unanalysable(f"gcloud run through {exe}")
    return found


def gcloud_invocations(tool_name: str, tool_input: dict) -> list[list[str]]:
    if tool_name.endswith(MCP_TOOL_SUFFIX):
        if isinstance(tool_input.get("args"), list):
            return [[str(a) for a in tool_input["args"]]]
        command = tool_input.get("command")
        if isinstance(command, str):
            argv = _tokens(command)
            return [argv[1:] if argv and Path(argv[0]).name == "gcloud" else argv]
        return []
    if tool_name == "Bash" and isinstance(tool_input.get("command"), str):
        return shell_gcloud_invocations(tool_input["command"])
    return []


def command_group(argv: list[str]) -> str | None:
    i = 0
    while i < len(argv):
        tok = argv[i]
        if tok.startswith("-"):
            i += 2 if (tok in VALUE_FLAGS and "=" not in tok) else 1
            continue
        if tok in ("alpha", "beta", "preview"):
            i += 1
            continue
        return tok
    return None


def project_flag(argv: list[str]) -> str | None:
    for i, a in enumerate(argv):
        if a.startswith("--project="):
            return a.split("=", 1)[1]
        if a == "--project" and i + 1 < len(argv):
            return argv[i + 1]
    return None


def is_project_scoped(argv: list[str]) -> bool:
    if any(a in HELP_FLAGS for a in argv):
        return False
    group = command_group(argv)
    return group is not None and group not in EXEMPT_GROUPS


NEGATION = re.compile(r"\b(not|don'?t|never|avoid|instead|except|rather than|no)\b", re.I)


def _answers(content) -> list[str]:
    """The selected answers in an AskUserQuestion result, never its question text."""
    text = content if isinstance(content, str) else json.dumps(content)
    try:
        data = json.loads(text)
        if isinstance(data, dict) and isinstance(data.get("answers"), dict):
            return [str(v) for v in data["answers"].values()]
    except ValueError:
        pass
    if isinstance(content, list):
        text = " ".join(str(b.get("text", "")) for b in content if isinstance(b, dict))
    return re.findall(r'"[^"]*"="([^"]*)"', text)


def user_turns(transcript_path: str | None) -> list[str]:
    """In order: messages the user typed, and their selected AskUserQuestion answers."""
    if not transcript_path:
        return []
    try:
        lines = Path(transcript_path).read_text(errors="replace").splitlines()
    except OSError:
        return []
    ask_ids: set[str] = set()
    turns: list[str] = []
    for line in lines:
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if not isinstance(entry, dict) or entry.get("isMeta") or entry.get("isCompactSummary"):
            continue
        message = entry.get("message")
        if not isinstance(message, dict):
            continue
        content = message.get("content")
        if entry.get("type") == "assistant" and isinstance(content, list):
            ask_ids |= {b.get("id") for b in content
                        if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") == "AskUserQuestion"}
        elif entry.get("type") == "user":
            blocks = [{"type": "text", "text": content}] if isinstance(content, str) else content
            for b in blocks if isinstance(blocks, list) else []:
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "text":
                    text = str(b.get("text", ""))
                    if not text.lstrip().startswith(("<command-", "<local-command", "<system-reminder", "<task-notification")):
                        turns.append(text)
                elif (b.get("type") == "tool_result" and b.get("tool_use_id") in ask_ids
                      and not b.get("is_error")):
                    turns += _answers(b.get("content"))
    return turns


def _names(text: str, project: str) -> bool:
    return re.search(rf"(?<![a-z0-9:.-]){re.escape(project)}(?![a-z0-9-])", text) is not None


def user_chose(project: str, candidates: list[str], transcript_path: str | None) -> bool:
    """True when the latest user turn naming any candidate names exactly this one, affirmatively."""
    pool = set(candidates) | {project}
    for turn in reversed(user_turns(transcript_path)):
        named = {c for c in pool if _names(turn, c)}
        if named:
            return named == {project} and not NEGATION.search(turn)
    return False


def needs_project(argv: list[str]) -> bool:
    if any(a == "--project" or a.startswith("--project=") for a in argv):
        return False
    if any(a in HELP_FLAGS for a in argv):
        return False
    group = command_group(argv)
    return group is not None and group not in EXEMPT_GROUPS


def resolve(cwd: Path) -> tuple[list[dict], dict]:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import preflight  # sibling script: the shared resolver
    candidates = preflight.collect_project_candidates(cwd)
    return candidates, preflight.resolve_project(candidates)


def guidance(cwd: Path, resolved: tuple[list[dict], dict] | None = None) -> str:
    candidates, result = resolved or resolve(cwd)
    by_value: dict[str, list[str]] = {}
    for c in candidates:
        if c["valid"]:
            by_value.setdefault(c["value"], []).append(c["source"])
    lines = [HEADER]
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


HEADER = "Blocked: this gcloud command is project-scoped and has no --project (gcp-project-context)."
FALLBACK = (HEADER + "\nThe project sources could not be read in time. Ask the user which project to use, "
            "then re-run with --project=PROJECT_ID.")


UNCONFIRMED = ("\nThe user has not chosen {project} in this session. Ask them to choose; "
               "re-run only with the project they name.")


def verdict(cwd: Path, scoped: list[list[str]], transcript_path: str | None) -> str | None:
    """Resolve the sources once and decide for every invocation in the event."""
    resolved = resolve(cwd)
    if any(project_flag(argv) is None for argv in scoped):
        return guidance(cwd, resolved)
    candidates, result = resolved
    if result["status"] != "conflict":
        return None
    for project in dict.fromkeys(project_flag(argv) for argv in scoped):
        if not user_chose(project, result["choices"], transcript_path):
            return guidance(cwd, resolved) + UNCONFIRMED.format(project=project)
    return None


def decide(event: dict) -> str | None:
    """Reason to block, or None to allow."""
    try:
        invocations = gcloud_invocations(str(event.get("tool_name", "")), event.get("tool_input") or {})
    except Unanalysable as exc:
        return (f"Blocked: {exc}; it cannot be checked for --project. Run each gcloud command on its own, "
                "with --project=PROJECT_ID (see gcp-project-context and gcloud-guardrails).")
    except ValueError:
        return None
    scoped = [argv for argv in invocations if is_project_scoped(argv)]
    if not scoped:
        return None
    cwd = Path(event.get("cwd") or Path.cwd())
    box: dict = {}

    def work() -> None:
        try:
            box["reason"] = verdict(cwd, scoped, event.get("transcript_path"))
        except Exception:  # resolver failure must still block, not crash open
            pass

    worker = threading.Thread(target=work, daemon=True)
    worker.start()
    worker.join(RESOLVE_BUDGET)  # one deadline for the whole event
    return box["reason"] if "reason" in box else FALLBACK


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except (ValueError, OSError):
        return  # not our input; never block on a parse failure
    if not isinstance(event, dict):
        return
    reason = decide(event)
    if reason:
        print(reason, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
