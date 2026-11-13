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


def _drift_errors(tmp_path, monkeypatch, manifest: str, mutate) -> list[str]:
    validator = _load_packaging_validator()
    for name in (".mcp.json", "mcp_config.json", "gemini-extension.json", "mcp.json"):
        (tmp_path / name).write_text((ROOT / name).read_text())
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
    assert any("developer-knowledge" in e for e in errors), errors


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
    assert any("differs" in e and "developer-knowledge" in e for e in errors), errors


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
