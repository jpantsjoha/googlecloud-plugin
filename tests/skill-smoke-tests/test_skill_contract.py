"""Smoke tests — the plugin must conform to Agent Plugins 1.0.0 and Agent Skills.

Specs under test:
  https://agent-plugins.org/specification
  https://agentskills.io/specification

Run: make test   (or: python -m pytest tests/skill-smoke-tests/ -v)
"""
import json
import re
import pytest
import yaml
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
SKILLS_DIR = ROOT / "skills"

SPEC_VERSION = "1.0.0"
PLUGIN_SCHEMA = f"https://agent-plugins.org/schemas/{SPEC_VERSION}/plugin.schema.json"
MCP_SCHEMA = f"https://agent-plugins.org/schemas/{SPEC_VERSION}/mcp.schema.json"

# Closed field sets — anything outside these makes the artefact non-conformant.
ALLOWED_SKILL_FIELDS = {
    "name", "description", "license", "allowed-tools", "metadata", "compatibility",
}
ALLOWED_PLUGIN_FIELDS = {
    "$schema", "name", "version", "description", "author",
    "homepage", "repository", "license", "keywords", "extensions",
}
NS = "googlecloud-plugin/"
REQUIRED_METADATA = {f"{NS}version", f"{NS}triggers", f"{NS}required-scopes"}
MAX_DESCRIPTION = 1024
EXPANDED = {"${PLUGIN_ROOT}", "${PLUGIN_DATA}"}


def skill_files() -> list[Path]:
    return sorted(SKILLS_DIR.glob("*/SKILL.md"))


def parse_frontmatter(path: Path) -> dict:
    content = path.read_text()
    assert content.startswith("---"), f"{path}: Missing YAML frontmatter"
    parts = content.split("---", 2)
    assert len(parts) >= 3, f"{path}: Malformed frontmatter (missing closing ---)"
    fm = yaml.safe_load(parts[1])
    assert isinstance(fm, dict), f"{path}: Frontmatter must be a YAML mapping"
    return fm


# ─── Agent Skills conformance ────────────────────────────────────────────────

@pytest.mark.parametrize("skill_file", skill_files(), ids=lambda p: p.parent.name)
def test_frontmatter_parses(skill_file: Path) -> None:
    assert parse_frontmatter(skill_file), f"{skill_file}: Frontmatter is empty"


@pytest.mark.parametrize("skill_file", skill_files(), ids=lambda p: p.parent.name)
def test_no_non_conformant_fields(skill_file: Path) -> None:
    """A skill carrying extra top-level keys MUST be skipped by a conformant client."""
    extra = sorted(set(parse_frontmatter(skill_file)) - ALLOWED_SKILL_FIELDS)
    assert not extra, (
        f"{skill_file}: non-conformant frontmatter fields {extra} — "
        f"Agent Skills allows only {sorted(ALLOWED_SKILL_FIELDS)}"
    )


@pytest.mark.parametrize("skill_file", skill_files(), ids=lambda p: p.parent.name)
def test_required_fields_present(skill_file: Path) -> None:
    fm = parse_frontmatter(skill_file)
    missing = [f for f in ("name", "description") if f not in fm]
    assert not missing, f"{skill_file}: Missing required fields: {missing}"


@pytest.mark.parametrize("skill_file", skill_files(), ids=lambda p: p.parent.name)
def test_name_matches_directory(skill_file: Path) -> None:
    fm = parse_frontmatter(skill_file)
    dir_name = skill_file.parent.name
    assert fm.get("name") == dir_name, (
        f"{skill_file}: name '{fm.get('name')}' does not match directory '{dir_name}'"
    )


@pytest.mark.parametrize("skill_file", skill_files(), ids=lambda p: p.parent.name)
def test_name_format(skill_file: Path) -> None:
    name = parse_frontmatter(skill_file)["name"]
    assert len(name) <= 64, f"{skill_file}: name exceeds 64 chars"
    assert name == name.lower(), f"{skill_file}: name must be lowercase"
    assert not name.startswith("-") and not name.endswith("-")
    assert "--" not in name, f"{skill_file}: consecutive hyphens in name"
    assert all(c.isalnum() or c == "-" for c in name)


@pytest.mark.parametrize("skill_file", skill_files(), ids=lambda p: p.parent.name)
def test_description_within_limit(skill_file: Path) -> None:
    description = parse_frontmatter(skill_file)["description"]
    assert description.strip(), f"{skill_file}: description must be non-empty"
    assert len(description) <= MAX_DESCRIPTION, (
        f"{skill_file}: description is {len(description)} chars, limit {MAX_DESCRIPTION}"
    )


# ─── Plugin contract, now carried under metadata ─────────────────────────────

@pytest.mark.parametrize("skill_file", skill_files(), ids=lambda p: p.parent.name)
def test_metadata_is_string_map(skill_file: Path) -> None:
    """Agent Skills defines metadata as a map from string keys to string values."""
    metadata = parse_frontmatter(skill_file).get("metadata")
    assert isinstance(metadata, dict), f"{skill_file}: 'metadata' must be a mapping"
    for key, value in metadata.items():
        assert isinstance(key, str), f"{skill_file}: metadata key {key!r} must be a string"
        assert isinstance(value, str), (
            f"{skill_file}: metadata['{key}'] must be a string, got {type(value).__name__}"
        )


@pytest.mark.parametrize("skill_file", skill_files(), ids=lambda p: p.parent.name)
def test_metadata_namespaced(skill_file: Path) -> None:
    metadata = parse_frontmatter(skill_file)["metadata"]
    unnamespaced = sorted(k for k in metadata if not k.startswith(NS))
    assert not unnamespaced, f"{skill_file}: metadata keys not namespaced: {unnamespaced}"


@pytest.mark.parametrize("skill_file", skill_files(), ids=lambda p: p.parent.name)
def test_required_metadata_present(skill_file: Path) -> None:
    metadata = parse_frontmatter(skill_file)["metadata"]
    missing = sorted(REQUIRED_METADATA - set(metadata))
    assert not missing, f"{skill_file}: missing metadata keys {missing}"


@pytest.mark.parametrize("skill_file", skill_files(), ids=lambda p: p.parent.name)
def test_triggers_non_empty(skill_file: Path) -> None:
    triggers = parse_frontmatter(skill_file)["metadata"][f"{NS}triggers"]
    assert triggers.strip(), f"{skill_file}: triggers must be non-empty"


@pytest.mark.parametrize("skill_file", skill_files(), ids=lambda p: p.parent.name)
def test_every_trigger_is_routable(skill_file: Path) -> None:
    """A trigger absent from the description is unroutable — no client reads metadata."""
    fm = parse_frontmatter(skill_file)
    description = fm["description"].lower()
    triggers = [t.strip() for t in fm["metadata"][f"{NS}triggers"].split(",") if t.strip()]
    unroutable = [t for t in triggers if t.lower() not in description]
    assert not unroutable, (
        f"{skill_file}: trigger(s) {unroutable} appear only in metadata, so a "
        f"conformant client routing on 'description' can never match them"
    )


@pytest.mark.parametrize("skill_file", skill_files(), ids=lambda p: p.parent.name)
def test_references_directory_exists(skill_file: Path) -> None:
    refs = skill_file.parent / "references"
    assert refs.is_dir(), f"{skill_file.parent}: Missing references/ directory"


# ─── Agent Plugins manifest conformance ──────────────────────────────────────

def test_plugin_manifest_declares_schema() -> None:
    manifest = json.loads((ROOT / "plugin.json").read_text())
    assert manifest.get("$schema") == PLUGIN_SCHEMA, (
        "plugin.json must declare the Agent Plugins manifest schema — it is a "
        "required field on a closed schema, so omitting it is a FATAL violation"
    )


def test_plugin_manifest_fields_permitted() -> None:
    manifest = json.loads((ROOT / "plugin.json").read_text())
    extra = sorted(set(manifest) - ALLOWED_PLUGIN_FIELDS)
    assert not extra, f"plugin.json has non-permitted top-level fields {extra}"


def test_plugin_name_pattern() -> None:
    name = json.loads((ROOT / "plugin.json").read_text())["name"]
    assert re.match(r"^(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$", name)
    assert 1 <= len(name) <= 64


def test_mcp_config_conforms() -> None:
    config = json.loads((ROOT / "mcp.json").read_text())
    assert config.get("$schema") == MCP_SCHEMA
    assert sorted(config) == ["$schema", "mcpServers"], (
        "mcp.json permits only '$schema' and 'mcpServers' at the top level"
    )
    assert config["mcpServers"], "mcp.json declares no servers"


def test_mcp_servers_declare_transport() -> None:
    """The schema discriminates transports on 'type' — a server without it is skipped."""
    servers = json.loads((ROOT / "mcp.json").read_text())["mcpServers"]
    for name, cfg in servers.items():
        assert cfg.get("type") in ("stdio", "streamable-http", "sse"), (
            f"mcp.json server '{name}' must declare a supported 'type'"
        )


def test_mcp_uses_only_expandable_placeholders() -> None:
    """Only ${PLUGIN_ROOT} and ${PLUGIN_DATA} expand; anything else stays literal."""
    servers = json.loads((ROOT / "mcp.json").read_text())["mcpServers"]
    for name, cfg in servers.items():
        candidates = list(cfg.get("args") or []) + list((cfg.get("env") or {}).values())
        if isinstance(cfg.get("cwd"), str):
            candidates.append(cfg["cwd"])
        for value in candidates:
            for found in re.findall(r"\$\{[^}]*\}", str(value)):
                assert found in EXPANDED, (
                    f"mcp.json server '{name}': placeholder {found} does not expand and "
                    f"would be passed through literally"
                )


def test_mcp_schema_version_matches_plugin() -> None:
    plugin = json.loads((ROOT / "plugin.json").read_text())["$schema"]
    mcp = json.loads((ROOT / "mcp.json").read_text())["$schema"]
    version = lambda s: re.search(r"/schemas/([^/]+)/", s).group(1)
    assert version(plugin) == version(mcp), (
        "mcp.json and plugin.json MUST target the same Agent Plugins version"
    )


def test_skills_discoverable_non_recursively() -> None:
    """Clients discover skills only at skills/*/SKILL.md — never deeper."""
    assert skill_files(), "no skills discoverable at skills/*/SKILL.md"
    buried = list(SKILLS_DIR.glob("*/*/**/SKILL.md"))
    assert not buried, f"SKILL.md below the discovery depth will be ignored: {buried}"


# ─── Harness MCP drift guard (scripts/validate_plugin.py) ────────────────────

HELPER_SOURCE = ROOT / "scripts" / "dk_adc_headers.py"


def _load_packaging_validator():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "validate_plugin", ROOT / "scripts" / "validate_plugin.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    "manifest,key",
    [(".mcp.json", "url"), ("mcp_config.json", "serverUrl"), ("gemini-extension.json", "httpUrl")],
)
def test_remote_url_read_under_native_key(manifest: str, key: str) -> None:
    validator = _load_packaging_validator()
    errors: list[str] = []
    assert validator.remote_url({key: "https://example.test/mcp"}, manifest, "srv", errors) == "https://example.test/mcp"
    assert errors == []


def test_harness_manifests_currently_agree() -> None:
    validator = _load_packaging_validator()
    errors: list[str] = []
    validator.check_mcp_consistency(errors)
    assert errors == []


def _copy_mcp_fixture(tmp_path: Path) -> None:
    for name in (".mcp.json", "mcp_config.json", "gemini-extension.json", "mcp.json"):
        (tmp_path / name).write_text((ROOT / name).read_text())
    (tmp_path / "scripts").mkdir(exist_ok=True)
    (tmp_path / "scripts" / "dk_adc_headers.py").write_text(HELPER_SOURCE.read_text())


def test_mcp_fixture_baseline_is_clean(tmp_path, monkeypatch) -> None:
    validator = _load_packaging_validator()
    _copy_mcp_fixture(tmp_path)
    monkeypatch.setattr(validator, "ROOT", tmp_path)
    errors: list[str] = []
    validator.check_mcp_consistency(errors)
    assert errors == []


def _drift_errors(tmp_path, monkeypatch, manifest: str, mutate) -> list[str]:
    validator = _load_packaging_validator()
    _copy_mcp_fixture(tmp_path)
    data = json.loads((tmp_path / manifest).read_text())
    mutate(data["mcpServers"]["developer-knowledge"])
    (tmp_path / manifest).write_text(json.dumps(data))
    monkeypatch.setattr(validator, "ROOT", tmp_path)
    errors: list[str] = []
    validator.check_mcp_consistency(errors)
    return errors


def test_remote_server_url_drift_is_caught(tmp_path, monkeypatch) -> None:
    """A remote server whose endpoint differs between harnesses must fail the gate."""
    def drift(cfg):
        cfg["serverUrl"] = "https://drifted.example.test/mcp"
    errors = _drift_errors(tmp_path, monkeypatch, "mcp_config.json", drift)
    assert any("MCP drift: server 'developer-knowledge' differs" in e for e in errors), errors


def test_foreign_endpoint_key_is_rejected(tmp_path, monkeypatch) -> None:
    """Swapping Gemini's httpUrl for Claude's `url` passes a naive compare but Gemini would not read it."""
    def swap(cfg):
        cfg["url"] = cfg.pop("httpUrl")
    errors = _drift_errors(tmp_path, monkeypatch, "gemini-extension.json", swap)
    assert any("reads only 'httpUrl'" in e for e in errors), errors


def test_matching_shadow_key_cannot_mask_native_drift(tmp_path, monkeypatch) -> None:
    def shadow(cfg):
        cfg["url"] = cfg["httpUrl"]
        cfg["httpUrl"] = "https://drifted.example.test/mcp"
    errors = _drift_errors(tmp_path, monkeypatch, "gemini-extension.json", shadow)
    assert any("reads only 'httpUrl'" in e for e in errors), errors
    assert any("MCP drift: server 'developer-knowledge' differs" in e for e in errors), errors


# ─── Auth: no key-file recipes (shared/auth/README.md, issue #16) ─────────────

# Shell continuations are joined first, so a recipe split across lines is still
# one command. Only fenced code is scanned: prose may name a flag to forbid it.
KEY_FILE_RECIPES = re.compile(
    r"gcloud\s+auth\s+activate-service-account\b[^\n]*--key-file"
    r"|gcloud\s+storage\s+sign-url\b[^\n]*--private-key-file"
    r"|gcloud\s+iam\s+service-accounts\s+keys\s+create\b"
)
FENCE = re.compile(r"```[^\n]*\n(.*?)```", re.S)


def key_file_recipes(text: str) -> list[str]:
    hits = []
    for block in FENCE.findall(text):
        joined = re.sub(r"\\\n\s*", " ", block)
        hits += [line.strip() for line in joined.splitlines() if KEY_FILE_RECIPES.search(line)]
    return hits


@pytest.mark.parametrize("snippet", [
    "```bash\ngcloud auth activate-service-account --key-file=/x/credentials.json\n```",
    "```bash\ngcloud auth activate-service-account \\\n  --key-file=/x/anything.json\n```",
    "```bash\ngcloud storage sign-url gs://b/o \\\n  --duration=1h \\\n  --private-key-file=k.json\n```",
    "```bash\ngcloud iam service-accounts keys create out.json --iam-account=SA\n```",
])
def test_key_file_guard_catches(snippet: str) -> None:
    assert key_file_recipes(snippet), snippet


@pytest.mark.parametrize("snippet", [
    "```bash\nexport GOOGLE_APPLICATION_CREDENTIALS=wif-credentials.json\n```",
    "```bash\nexport GOOGLE_APPLICATION_CREDENTIALS=sa-keyless-wif.json\n```",
    "Never use `--private-key-file` or `activate-service-account --key-file`.",
    "```bash\ngcloud storage sign-url gs://b/o --impersonate-service-account=SA\n```",
])
def test_key_file_guard_allows(snippet: str) -> None:
    assert not key_file_recipes(snippet), snippet


def test_no_service_account_key_recipes() -> None:
    """Examples must use impersonation, attached service accounts or Workload Identity Federation."""
    offenders = []
    for path in [*SKILLS_DIR.glob("*/SKILL.md"), *SKILLS_DIR.glob("*/references/*.md"),
                 *(ROOT / "shared").rglob("*.md"), ROOT / "PLUGIN.md", ROOT / "AGENTS.md", ROOT / "GEMINI.md"]:
        offenders += [f"{path.relative_to(ROOT)}: {hit}" for hit in key_file_recipes(path.read_text())]
    assert not offenders, "service-account key recipe found:\n" + "\n".join(offenders)


# ─── Codex plugin manifest (issue #17) ───────────────────────────────────────

def _codex_errors(tmp_path, monkeypatch, mutate) -> list[str]:
    """Validate a mutated copy; `mutate` may edit the dict in place or return a replacement."""
    validator = _load_packaging_validator()
    tmp_path = tmp_path / "repo"
    (tmp_path / ".codex-plugin").mkdir(parents=True)
    (tmp_path / "skills").mkdir()
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "logo.svg").write_text((ROOT / "assets" / "logo.svg").read_text())
    data = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text())
    if mutate == "ABSOLUTE":  # absolute path to a real skills dir inside this checkout
        mutate = lambda d: d.update(skills=str((tmp_path / "skills").resolve()))
    replaced = mutate(data)
    data = data if replaced is None else replaced
    text = "null" if data == "null" else json.dumps(data)
    (tmp_path / ".codex-plugin" / "plugin.json").write_text(text)
    monkeypatch.setattr(validator, "ROOT", tmp_path)
    errors: list[str] = []
    validator.check_codex(errors)
    return [e for e in errors if e.startswith("codex plugin.json")]


def test_codex_manifest_currently_valid(tmp_path, monkeypatch) -> None:
    assert _codex_errors(tmp_path, monkeypatch, lambda d: None) == []


@pytest.mark.parametrize("mutate,expected", [
    (lambda d: d.update(version="9.9.9"), "version"),
    (lambda d: d.update(skills="./nowhere/"), "skills path"),
    (lambda d: d["interface"].pop("displayName") and None, "displayName"),
    (lambda d: d.update(skills="../skills/"), "skills path"),
    (lambda d: d.update(skills="./"), "skills path"),
    (lambda d: d.update(skills=["./skills/"]), "skills path"),
    (lambda d: d.update(interface="GoogleCloud Plugin"), "must be an object"),
    (lambda d: d["interface"].update(displayName=42), "displayName"),
    (lambda d: {}, "name"),
    ("ABSOLUTE", "skills path"),
    (lambda d: "null", "JSON object"),
])
def test_codex_manifest_drift_is_caught(tmp_path, monkeypatch, mutate, expected) -> None:
    errors = _codex_errors(tmp_path, monkeypatch, mutate)
    assert any(expected in e for e in errors), errors


# ─── Link checker: MCP endpoints (scripts/check_links.py) ────────────────────

def _load_link_checker():
    import importlib.util
    spec = importlib.util.spec_from_file_location("check_links", ROOT / "scripts" / "check_links.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("url,status,ok", [
    ("https://cloudcli.googleapis.com/mcp", 405, True),
    ("https://developerknowledge.googleapis.com/mcp", 401, True),
    ("https://cloudcli.googleapis.com/mcp", 403, True),
    ("https://cloudcli.googleapis.com/mcp", 404, False),
    ("https://example.test/mcp", 405, False),
    ("https://cloudcli.googleapis.com/mcp/", 405, False),
    ("https://cloudcli.googleapis.com/mcp", 0, False),
    ("https://cloud.google.com/run/docs", 405, False),
    ("https://cloud.google.com/run/docs", 200, True),
])
def test_link_checker_mcp_endpoints(url: str, status: int, ok: bool) -> None:
    assert _load_link_checker().resolved(url, status) is ok


# ─── Developer Knowledge ADC headers helper (scripts/dk_adc_headers.py) ──────

import os
import subprocess
import sys

HELPER = ROOT / "scripts" / "dk_adc_headers.py"


def _fake_gcloud(bin_dir: Path, token: str | None, project: str | None = "proj-123") -> None:
    """A stand-in gcloud: prints a token (or fails) and a project (or fails)."""
    bin_dir.mkdir(parents=True, exist_ok=True)
    script = bin_dir / "gcloud"
    token_branch = f'echo "{token}"; exit 0' if token else 'echo "not logged in" >&2; exit 1'
    project_branch = f'echo "{project}"; exit 0' if project else 'echo "error" >&2; exit 1'
    script.write_text(
        "#!/bin/sh\n"
        'case "$*" in\n'
        f'  "auth application-default print-access-token") {token_branch};;\n'
        f'  "config get-value project") {project_branch};;\n'
        "esac\nexit 1\n"
    )
    script.chmod(0o755)


def _run_helper(tmp_path: Path, path_dirs: list[Path], adc: dict | None = None) -> dict:
    config = tmp_path / "gcloud-config"
    config.mkdir(exist_ok=True)
    if adc is not None:
        (config / "application_default_credentials.json").write_text(json.dumps(adc))
    env = {"PATH": os.pathsep.join(str(p) for p in path_dirs), "CLOUDSDK_CONFIG": str(config), "HOME": str(tmp_path)}
    out = subprocess.run([sys.executable, str(HELPER)], capture_output=True, text=True, env=env, timeout=20)
    assert out.returncode == 0, out.stderr
    assert out.stderr == "", "the helper must not write to stderr"
    return json.loads(out.stdout)


def test_helper_emits_bearer_and_quota_project(tmp_path) -> None:
    _fake_gcloud(tmp_path / "bin", token="tok-abc")
    assert _run_helper(tmp_path, [tmp_path / "bin"]) == {
        "Authorization": "Bearer tok-abc", "X-Goog-User-Project": "proj-123"}


def test_helper_prefers_adc_quota_project(tmp_path) -> None:
    _fake_gcloud(tmp_path / "bin", token="tok-abc")
    headers = _run_helper(tmp_path, [tmp_path / "bin"], adc={"quota_project_id": "quota-proj"})
    assert headers["X-Goog-User-Project"] == "quota-proj"


@pytest.mark.parametrize("project", ["(unset)", None])
def test_helper_empty_without_quota_project(tmp_path, project) -> None:
    """A token without a quota project is refused, so emit nothing and let the key header apply."""
    _fake_gcloud(tmp_path / "bin", token="tok-abc", project=project)
    assert _run_helper(tmp_path, [tmp_path / "bin"]) == {}


def test_helper_empty_when_not_logged_in(tmp_path) -> None:
    _fake_gcloud(tmp_path / "bin", token=None)
    assert _run_helper(tmp_path, [tmp_path / "bin"]) == {}


def test_helper_empty_without_gcloud(tmp_path) -> None:
    (tmp_path / "empty").mkdir()
    assert _run_helper(tmp_path, [tmp_path / "empty"]) == {}


def test_helper_wired_in_claude_manifest() -> None:
    server = json.loads((ROOT / ".mcp.json").read_text())["mcpServers"]["developer-knowledge"]
    assert server.get("headersHelper") == "python3 scripts/dk_adc_headers.py"
    assert "X-Goog-Api-Key" in server.get("headers", {}), "static key header stays as the fallback"


# ─── Logo and helper path checks (scripts/validate_plugin.py) ────────────────

def test_logo_is_square_svg() -> None:
    import xml.etree.ElementTree as ET
    root = ET.parse(ROOT / "assets" / "logo.svg").getroot()
    _, _, width, height = (float(n) for n in root.get("viewBox").split())
    assert width == height, "listing icons must be square"


@pytest.mark.parametrize("value,ok", [
    ("./assets/logo.svg", True),
    ("assets/logo.svg", True),
    ("./assets/missing.svg", False),
    ("../assets/logo.svg", False),
    (str(ROOT / "assets" / "logo.svg"), False),
    (42, False),
])
def test_repo_file_resolves(value, ok) -> None:
    assert _load_packaging_validator().repo_file_resolves(value) is ok


def test_broken_icon_and_helper_paths_are_caught(tmp_path, monkeypatch) -> None:
    validator = _load_packaging_validator()
    errors: list[str] = []
    validator.check_icon_fields("codex plugin.json", {"logo": "./assets/missing.svg"}, errors)
    assert any("logo" in e for e in errors), errors
    _copy_mcp_fixture(tmp_path)
    data = json.loads((tmp_path / ".mcp.json").read_text())
    data["mcpServers"]["developer-knowledge"]["headersHelper"] = "python3 scripts/missing.py"
    (tmp_path / ".mcp.json").write_text(json.dumps(data))
    monkeypatch.setattr(validator, "ROOT", tmp_path)
    errors = []
    validator.check_mcp_consistency(errors)
    assert any("headersHelper" in e for e in errors), errors


# ─── Project resolution (scripts/preflight.py, gcp-project-context) ──────────

PREFLIGHT = ROOT / "scripts" / "preflight.py"


def _load_preflight():
    import importlib.util
    spec = importlib.util.spec_from_file_location("preflight", PREFLIGHT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _gcloud_stub(bin_dir: Path, project: str | None, configuration: str = "default",
                 account: str | None = "dev@example.com") -> Path:
    """Behaves like gcloud: an exported CLOUDSDK_CORE_PROJECT overrides the stored project."""
    bin_dir.mkdir(parents=True, exist_ok=True)
    script = bin_dir / "gcloud"
    stored = f'echo "{project}"' if project else 'echo "(unset)"'
    proj = f'if [ -n "$CLOUDSDK_CORE_PROJECT" ]; then echo "$CLOUDSDK_CORE_PROJECT"; else {stored}; fi'
    script.write_text(
        "#!/bin/sh\n"
        'case "$*" in\n'
        f'  "config get-value project") {proj};;\n'
        f'  "config configurations list --filter=is_active=true --format=value(name)") echo "{configuration}";;\n'
        f'  "config get-value account") echo "{account or "(unset)"}";;\n'
        '  "version") echo "Google Cloud SDK 0.0.0";;\n'
        "esac\nexit 0\n"
    )
    script.chmod(0o755)
    return bin_dir


def _candidates(tmp_path, monkeypatch, env: dict, dotenv: str | None = None, gcloud_project: str | None = None):
    preflight = _load_preflight()
    monkeypatch.setenv("PATH", str(_gcloud_stub(tmp_path / "bin", gcloud_project)))
    for var in preflight.PROJECT_ENV_VARS:
        if var in env:
            monkeypatch.setenv(var, env[var])
        else:
            monkeypatch.delenv(var, raising=False)
    repo = tmp_path / "repo"
    repo.mkdir(exist_ok=True)
    if dotenv is not None:
        (repo / ".env").write_text(dotenv)
    found = preflight.collect_project_candidates(repo, env=env)
    return found, preflight.resolve_project(found)


def test_project_resolved_when_sources_agree(tmp_path, monkeypatch) -> None:
    found, result = _candidates(tmp_path, monkeypatch, {"GOOGLE_CLOUD_PROJECT": "alpha-proj"},
                                dotenv="GCP_PROJECT_ID=alpha-proj\n", gcloud_project="alpha-proj")
    assert result["status"] == "resolved" and result["project"] == "alpha-proj"
    assert [c["source"] for c in found] == ["env:GOOGLE_CLOUD_PROJECT", ".env:GCP_PROJECT_ID", "gcloud config (default)"]


def test_project_conflict_lists_every_choice(tmp_path, monkeypatch) -> None:
    _, result = _candidates(tmp_path, monkeypatch, {"CLOUDSDK_CORE_PROJECT": "alpha-proj"},
                            dotenv="export GOOGLE_CLOUD_PROJECT='beta-proj'  # app\n", gcloud_project="gamma-proj")
    assert result["status"] == "conflict"
    assert result["choices"] == ["alpha-proj", "beta-proj", "gamma-proj"]
    assert result["gcloud_uses"] == "alpha-proj", "CLOUDSDK_CORE_PROJECT overrides the configuration"


def test_project_missing(tmp_path, monkeypatch) -> None:
    _, result = _candidates(tmp_path, monkeypatch, {}, gcloud_project=None)
    assert result["status"] == "missing" and result["choices"] == []


def test_unexpanded_placeholder_is_invalid_not_a_project(tmp_path, monkeypatch) -> None:
    found, result = _candidates(tmp_path, monkeypatch, {"CLOUDSDK_CORE_PROJECT": "${GCP_PROJECT_ID}"},
                                gcloud_project="alpha-proj")
    assert result["status"] == "resolved" and result["project"] == "alpha-proj"
    assert [c["value"] for c in result["invalid"]] == ["${GCP_PROJECT_ID}"]


def test_override_does_not_hide_stored_configuration(tmp_path, monkeypatch) -> None:
    """With CLOUDSDK_CORE_PROJECT exported, the stored configuration project is still read and reported."""
    found, result = _candidates(tmp_path, monkeypatch, {"CLOUDSDK_CORE_PROJECT": "alpha-proj"}, gcloud_project="beta-proj")
    assert [(c["source"], c["value"]) for c in found] == [
        ("env:CLOUDSDK_CORE_PROJECT", "alpha-proj"), ("gcloud config (default)", "beta-proj")]
    assert result["status"] == "conflict" and result["gcloud_uses"] == "alpha-proj"


def test_legacy_domain_scoped_id_is_valid(tmp_path, monkeypatch) -> None:
    _, alone = _candidates(tmp_path, monkeypatch, {"GOOGLE_CLOUD_PROJECT": "example.com:legacy-proj"})
    assert alone["status"] == "resolved" and alone["project"] == "example.com:legacy-proj"
    _, both = _candidates(tmp_path, monkeypatch, {"GOOGLE_CLOUD_PROJECT": "example.com:legacy-proj"},
                          dotenv="GCP_PROJECT_ID=alpha-proj\n")
    assert both["status"] == "conflict"


@pytest.mark.parametrize("text,expected", [
    ("GOOGLE_CLOUD_PROJECT=beta-proj\t# app\n", [("GOOGLE_CLOUD_PROJECT", "beta-proj")]),
    ("GOOGLE_CLOUD_PROJECT=beta-proj # app\r\n", [("GOOGLE_CLOUD_PROJECT", "beta-proj")]),
    ("export GCP_PROJECT_ID='beta-proj'\n", [("GCP_PROJECT_ID", "beta-proj")]),
    ('GCLOUD_PROJECT="beta-proj # suffix"\n', [("GCLOUD_PROJECT", "beta-proj # suffix")]),
    ('CLOUDSDK_CORE_PROJECT="unclosed\nAPI_SECRET=do-not-print\n',
     [("CLOUDSDK_CORE_PROJECT", "<unterminated quoted value>")]),
    ('TOKEN="first \\"\nGCP_PROJECT_ID=leaked-value\nlast"\nGOOGLE_CLOUD_PROJECT=real-proj\n',
     [("GOOGLE_CLOUD_PROJECT", "real-proj")]),
    ("TOKEN='single \\'\nGOOGLE_CLOUD_PROJECT=real-proj\n", [("GOOGLE_CLOUD_PROJECT", "real-proj")]),
    ("# GOOGLE_CLOUD_PROJECT=commented-out\n", []),
    ('SECRET="first\nGCP_PROJECT_ID=inside-secret\nlast"\nGOOGLE_CLOUD_PROJECT=real-proj\n',
     [("GOOGLE_CLOUD_PROJECT", "real-proj")]),
])
def test_dotenv_parser(text, expected) -> None:
    assert _load_preflight().parse_dotenv_projects(text) == expected


@pytest.mark.parametrize("dotenv", [
    'GOOGLE_CLOUD_PROJECT="unclosed\nAPI_SECRET=do-not-print\n',
    'TOKEN="a \\"\nGCP_PROJECT_ID=do-not-print\nz"\nGOOGLE_CLOUD_PROJECT=alpha-proj\n',
])
@pytest.mark.parametrize("as_json", [True, False])
def test_preflight_output_never_leaks_dotenv_secrets(tmp_path, dotenv, as_json) -> None:
    bin_dir = _gcloud_stub(tmp_path / "bin", "alpha-proj")
    home = tmp_path / "home"
    (home / ".config" / "gcloud").mkdir(parents=True)
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".env").write_text(dotenv)
    args = [sys.executable, str(PREFLIGHT), "--project-dir", str(repo)] + (["--json"] if as_json else [])
    out = subprocess.run(args, capture_output=True, text=True, timeout=30, env={"PATH": str(bin_dir), "HOME": str(home)})
    assert "do-not-print" not in out.stdout + out.stderr


def test_quoted_comment_value_is_invalid_not_truncated(tmp_path, monkeypatch) -> None:
    _, result = _candidates(tmp_path, monkeypatch, {}, dotenv='GOOGLE_CLOUD_PROJECT="beta-proj # x"\n',
                            gcloud_project="alpha-proj")
    assert result["status"] == "resolved" and result["project"] == "alpha-proj"
    assert [c["value"] for c in result["invalid"]] == ["beta-proj # x"]


def test_dotenv_reads_only_project_keys(tmp_path, monkeypatch) -> None:
    found, _ = _candidates(tmp_path, monkeypatch, {},
                           dotenv='API_SECRET=do-not-read\nTOKEN="multi\nGCP_PROJECT_ID=leaked-value\nline"\n'
                                  "GOOGLE_CLOUD_PROJECT=alpha-proj\n")
    dumped = json.dumps(found)
    assert "do-not-read" not in dumped and "leaked-value" not in dumped


@pytest.mark.parametrize("env,gcloud_project,creds,code,status", [
    ({"GOOGLE_CLOUD_PROJECT": "alpha-proj"}, "alpha-proj", True, 0, "resolved"),
    ({"GOOGLE_CLOUD_PROJECT": "alpha-proj"}, "beta-proj", True, 3, "conflict"),
    ({}, None, True, 2, "missing"),
    ({"GOOGLE_CLOUD_PROJECT": "alpha-proj"}, "alpha-proj", False, 2, "resolved"),
])
def test_preflight_cli_exit_codes(tmp_path, env, gcloud_project, creds, code, status) -> None:
    """Exit 0 ready, 3 project conflict, 2 project or credentials missing."""
    bin_dir = _gcloud_stub(tmp_path / "bin", gcloud_project, account="dev@example.com" if creds else None)
    home = tmp_path / "home"
    (home / ".config" / "gcloud").mkdir(parents=True)
    if creds:
        (home / ".config" / "gcloud" / "application_default_credentials.json").write_text("{}")
    repo = tmp_path / "repo"
    repo.mkdir()
    out = subprocess.run([sys.executable, str(PREFLIGHT), "--project-dir", str(repo), "--json"],
                         capture_output=True, text=True, timeout=30,
                         env={"PATH": str(bin_dir), "HOME": str(home), **env})
    assert out.returncode == code, out.stdout + out.stderr
    assert json.loads(out.stdout)["project"]["status"] == status


# ─── Harness manifests pass no placeholders into server env ──────────────────

@pytest.mark.parametrize("manifest", [".mcp.json", "mcp_config.json", "gemini-extension.json"])
def test_no_placeholder_in_server_env(manifest: str) -> None:
    """An unset ${VAR} reaches the server literally (observed: gcloud core.project='${GCP_PROJECT_ID}')."""
    servers = json.loads((ROOT / manifest).read_text())["mcpServers"]
    for name, cfg in servers.items():
        for key, value in (cfg.get("env") or {}).items():
            if not key.startswith("_"):
                assert "${" not in str(value), f"{manifest} server '{name}' env {key}={value}"
        for arg in cfg.get("args") or []:
            assert "${" not in str(arg), f"{manifest} server '{name}' arg {arg}"


@pytest.mark.parametrize("manifest", [".mcp.json", "mcp_config.json", "gemini-extension.json"])
def test_toolbox_not_shipped(manifest: str) -> None:
    assert "toolbox" not in json.loads((ROOT / manifest).read_text())["mcpServers"]


# ─── PreToolUse project guard (scripts/gcloud_project_guard.py) ──────────────

GUARD = ROOT / "scripts" / "gcloud_project_guard.py"
MCP_TOOL = "mcp__plugin_googlecloud-plugin_gcloud__run_gcloud_command"


def _load_guard():
    import importlib.util
    spec = importlib.util.spec_from_file_location("gcloud_project_guard", GUARD)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _blocked(tool, tool_input) -> bool:
    guard = _load_guard()
    try:
        invocations = guard.gcloud_invocations(tool, tool_input)
    except guard.Unanalysable:
        return True
    return any(guard.needs_project(argv) for argv in invocations)


@pytest.mark.parametrize("tool,tool_input,blocked", [
    (MCP_TOOL, {"args": ["run", "services", "list"]}, True),
    (MCP_TOOL, {"command": "gcloud run services list"}, True),
    (MCP_TOOL, {"args": ["run", "services", "list", "--project=alpha-proj"]}, False),
    (MCP_TOOL, {"args": ["run", "services", "list", "--project", "alpha-proj"]}, False),
    (MCP_TOOL, {"args": ["run", "services", "list", "--billing-project=quota-proj"]}, True),
    (MCP_TOOL, {"args": ["config", "list", "--format=json"]}, False),
    (MCP_TOOL, {"args": ["projects", "describe", "alpha-proj"]}, False),
    (MCP_TOOL, {"args": ["beta", "run", "services", "list"]}, True),
    (MCP_TOOL, {"args": ["--configuration", "config", "run", "services", "list"]}, True),
    (MCP_TOOL, {"args": ["--format", "json", "projects", "list"]}, False),
    (MCP_TOOL, {"args": ["-q", "run", "services", "list"]}, True),
    (MCP_TOOL, {"args": ["run", "deploy", "--help"]}, False),
    ("Bash", {"command": "gcloud compute instances list --limit=5"}, True),
    ("Bash", {"command": "gcloud compute instances list --help"}, False),
    ("Bash", {"command": "CLOUDSDK_CORE_PROJECT=x gcloud compute instances list"}, True),
    ("Bash", {"command": "env -u CLOUDSDK_CORE_PROJECT gcloud config get-value project"}, False),
    ("Bash", {"command": "/usr/local/bin/gcloud sql instances list --project=alpha-proj"}, False),
    ("Bash", {"command": "sh -c 'gcloud run services list'"}, True),
    ("Bash", {"command": "bash -c \"gcloud run services list --project=alpha-proj\""}, False),
    ("Bash", {"command": "true && gcloud run services list"}, True),
    ("Bash", {"command": "printf x | gcloud run services list"}, True),
    ("Bash", {"command": "gcloud config list && gcloud run services list"}, True),
    ("Bash", {"command": "gcloud run services list && printf '%s' '--project=decoy'"}, True),
    ("Bash", {"command": "sudo -E timeout 30 gcloud run services list"}, True),
    ("Bash", {"command": "echo $(gcloud run services list)"}, True),
    ("Bash", {"command": "eval 'gcloud run services list'"}, True),
    ("Bash", {"command": "ls -la && echo gcloud"}, False),
    ("Bash", {"command": "grep -r gcloud docs/"}, False),
    ("Bash", {"command": "bash -lc 'gcloud run services list'"}, True),
    ("Bash", {"command": "bash -lc 'gcloud run services list --project=alpha-proj'"}, False),
    ("Bash", {"command": "sudo -u root gcloud run services list"}, True),
    ("Bash", {"command": "if true; then gcloud run services list; fi"}, True),
    ("Bash", {"command": "for p in a b; do gcloud run services list; done"}, True),
    ("Bash", {"command": "if true; then gcloud run services list --project=alpha-proj; fi"}, False),
    ("Bash", {"command": "ssh box 'gcloud run services list'"}, True),
    ("Bash", {"command": "sh -c \"sh -c 'sh -c \\\"sh -c gcloud\\\"'\""}, True),
    ("Bash", {"command": "echo 'gcloud run services list'"}, False),
    ("Bash", {"command": "python3 -c 'import subprocess; subprocess.run([\"gcloud\", \"run\", \"services\", \"list\"])'"}, True),
    ("Bash", {"command": "find . -exec gcloud run services list \\;"}, True),
    ("Bash", {"command": "awk 'BEGIN { system(\"gcloud run services list\") }'"}, True),
    ("Bash", {"command": "git commit -m 'docs: gcloud run services list example'"}, False),
    ("Bash", {"command": "gcloud help run deploy"}, False),
    ("Read", {"file_path": "/tmp/x"}, False),
])
def test_guard_classification(tool, tool_input, blocked) -> None:
    assert _blocked(tool, tool_input) is blocked


def test_guard_falls_back_to_blocking_when_resolution_fails(monkeypatch) -> None:
    guard = _load_guard()
    def boom(cwd):
        raise RuntimeError("resolver failed")
    monkeypatch.setattr(guard, "resolve", lambda cwd: ([], {"status": "resolved"}))
    monkeypatch.setattr(guard, "guidance", boom)
    reason = guard.decide({"tool_name": MCP_TOOL, "tool_input": {"args": ["run", "services", "list"]}, "cwd": "/tmp"})
    assert reason == guard.FALLBACK


def test_guard_falls_back_to_blocking_when_resolution_is_slow(monkeypatch) -> None:
    import time as _time
    guard = _load_guard()
    monkeypatch.setattr(guard, "RESOLVE_BUDGET", 0.2)
    monkeypatch.setattr(guard, "resolve", lambda cwd: (_time.sleep(2), ([], {}))[1])
    reason = guard.decide({"tool_name": MCP_TOOL, "tool_input": {"args": ["run", "services", "list"]}, "cwd": "/tmp"})
    assert reason == guard.FALLBACK


def _run_guard(tmp_path, event: dict, gcloud_project: str | None, dotenv: str | None = None):
    bin_dir = _gcloud_stub(tmp_path / "bin", gcloud_project)
    repo = tmp_path / "repo"
    repo.mkdir(exist_ok=True)
    if dotenv:
        (repo / ".env").write_text(dotenv)
    event = {**event, "cwd": str(repo)}
    return subprocess.run([sys.executable, str(GUARD)], input=json.dumps(event), capture_output=True,
                          text=True, timeout=30, env={"PATH": str(bin_dir), "HOME": str(tmp_path)})


def test_guard_blocks_with_single_project_hint(tmp_path) -> None:
    out = _run_guard(tmp_path, {"tool_name": MCP_TOOL, "tool_input": {"args": ["run", "services", "list"]}}, "alpha-proj")
    assert out.returncode == 2 and "--project=alpha-proj" in out.stderr


def test_guard_blocks_and_asks_on_conflict(tmp_path) -> None:
    out = _run_guard(tmp_path, {"tool_name": MCP_TOOL, "tool_input": {"args": ["run", "services", "list"]}},
                     "alpha-proj", dotenv="API_SECRET=do-not-print\nGOOGLE_CLOUD_PROJECT=beta-proj\n")
    assert out.returncode == 2
    assert "Ask the user" in out.stderr and "alpha-proj" in out.stderr and "beta-proj" in out.stderr
    assert "do-not-print" not in out.stderr + out.stdout


def test_guard_blocks_and_suggests_init_when_missing(tmp_path) -> None:
    out = _run_guard(tmp_path, {"tool_name": MCP_TOOL, "tool_input": {"args": ["run", "services", "list"]}}, None)
    assert out.returncode == 2 and "gcloud init" in out.stderr


def test_guard_allows_explicit_project_and_bad_input(tmp_path) -> None:
    ok = _run_guard(tmp_path, {"tool_name": MCP_TOOL, "tool_input": {"args": ["run", "services", "list", "--project=beta-proj"]}}, "alpha-proj")
    assert ok.returncode == 0 and ok.stderr == ""
    junk = subprocess.run([sys.executable, str(GUARD)], input="not json", capture_output=True, text=True, timeout=30)
    assert junk.returncode == 0, "a malformed event must never block"


def test_hooks_manifest_wires_the_guard() -> None:
    hooks = json.loads((ROOT / "hooks" / "hooks.json").read_text())["hooks"]["PreToolUse"]
    entry = next(h for h in hooks if MCP_TOOL in h["matcher"].split("|"))
    assert "Bash" in entry["matcher"].split("|")
    handler = entry["hooks"][0]
    assert handler["command"] == "python3"
    assert handler["args"] == ["${CLAUDE_PLUGIN_ROOT}/scripts/gcloud_project_guard.py"]
    assert GUARD.is_file()


# ─── Conflict: explicit --project needs the user's own choice ────────────────

def _transcript(tmp_path: Path, entries: list[dict]) -> str:
    path = tmp_path / "transcript.jsonl"
    path.write_text("\n".join(json.dumps(e) for e in entries) + "\n")
    return str(path)


def _user(text):
    return {"type": "user", "message": {"role": "user", "content": text}}


def _assistant_text(text):
    return {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": text}]}}


def _tool_use(tool_id, name):
    return {"type": "assistant", "message": {"role": "assistant",
            "content": [{"type": "tool_use", "id": tool_id, "name": name, "input": {}}]}}


def _tool_result(tool_id, text):
    return {"type": "user", "message": {"role": "user",
            "content": [{"type": "tool_result", "tool_use_id": tool_id, "content": text}]}}


CONFLICT_DOTENV = "GOOGLE_CLOUD_PROJECT=beta-proj\n"
EXPLICIT = {"tool_name": MCP_TOOL, "tool_input": {"args": ["run", "services", "list", "--project=alpha-proj"]}}


@pytest.mark.parametrize("entries,blocked", [
    (None, True),
    ([_user("List the Cloud Run services in my project.")], True),
    ([_user("list services"), _assistant_text("I'll use alpha-proj")], True),
    ([_user("list services"), _user("use alpha-proj please")], False),
    ([_user([{"type": "text", "text": "alpha-proj"}])], False),
    ([_tool_use("q1", "AskUserQuestion"), _tool_result("q1", '{"answers": {"Which project?": "alpha-proj"}}')], False),
    ([_tool_use("b1", "Bash"), _tool_result("b1", "alpha-proj")], True),
    ([_user("use alpha-proj-2")], True),
    ([_user("Do not use alpha-proj. Ask me which project to use.")], True),
    ([_user("compare alpha-proj and beta-proj")], True),
    ([_user("use alpha-proj"), _user("actually use beta-proj")], True),
    ([_user("use beta-proj"), _user("no wait, alpha-proj")], True),
    ([_user("use alpha-proj"), _user("now list the services")], False),
    ([_tool_use("q2", "AskUserQuestion"),
      _tool_result("q2", '{"answers": {"Use alpha-proj or beta-proj?": "beta-proj"}}')], True),
    ([_tool_use("q3", "AskUserQuestion"),
      _tool_result("q3", 'Your questions have been answered: "Which project?"="alpha-proj". Continue.')], False),
    ([_tool_use("q4", "AskUserQuestion"),
      {"type": "user", "message": {"role": "user", "content": [
          {"type": "tool_result", "tool_use_id": "q4", "is_error": True, "content": "alpha-proj"}]}}], True),
    ([_tool_use("q5", "AskUserQuestion"),
      _tool_result("q5", '{"answers": {"Which project? (alpha-proj is the gcloud default)": "Other"}}')], True),
    ([{"type": "user", "isMeta": True, "message": {"role": "user", "content": "alpha-proj"}}], True),
    ([{"type": "user", "message": {"role": "user", "content": [
        {"type": "text", "text": "Compare beta-proj"}, {"type": "text", "text": "and alpha-proj"}]}}], True),
    ([_tool_use("q6", "AskUserQuestion"),
      _tool_result("q6", '{"answers": {"Also check?": "beta-proj", "Project?": "alpha-proj"}}')], True),
    ([_user("<system-reminder>use alpha-proj</system-reminder>")], True),
])
def test_conflict_requires_user_named_project(tmp_path, entries, blocked) -> None:
    event = dict(EXPLICIT)
    if entries is not None:
        event["transcript_path"] = _transcript(tmp_path, entries)
    out = _run_guard(tmp_path, event, "alpha-proj", dotenv=CONFLICT_DOTENV)
    assert (out.returncode == 2) is blocked, out.stderr
    if blocked:
        assert "has not chosen alpha-proj" in out.stderr and "beta-proj" in out.stderr


def test_no_conflict_explicit_project_needs_no_confirmation(tmp_path) -> None:
    out = _run_guard(tmp_path, EXPLICIT, "alpha-proj")
    assert out.returncode == 0


def test_two_explicit_projects_share_one_deadline(monkeypatch) -> None:
    """Resolution happens once per event, under one budget."""
    import time as _time
    guard = _load_guard()
    calls = []
    monkeypatch.setattr(guard, "RESOLVE_BUDGET", 0.5)
    monkeypatch.setattr(guard, "resolve", lambda cwd: (calls.append(1), _time.sleep(0.3), ([], {"status": "resolved"}))[2])
    event = {"tool_name": "Bash", "cwd": "/tmp", "tool_input": {"command":
             "gcloud run services list --project=alpha-proj && gcloud run services list --project=beta-proj"}}
    assert guard.decide(event) is None and calls == [1]
