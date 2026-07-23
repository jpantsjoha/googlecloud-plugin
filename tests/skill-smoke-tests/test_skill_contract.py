"""Smoke tests — every SKILL.md must conform to the plugin contract.

Run: make test   (or: python -m pytest tests/skill-smoke-tests/ -v)
"""
import pytest
import yaml
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent.parent / "skills"
REQUIRED_FIELDS = ["name", "description", "version", "triggers", "required_scopes"]


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


@pytest.mark.parametrize("skill_file", skill_files(), ids=lambda p: p.parent.name)
def test_frontmatter_parses(skill_file: Path) -> None:
    fm = parse_frontmatter(skill_file)
    assert fm, f"{skill_file}: Frontmatter is empty"


@pytest.mark.parametrize("skill_file", skill_files(), ids=lambda p: p.parent.name)
def test_required_fields_present(skill_file: Path) -> None:
    fm = parse_frontmatter(skill_file)
    missing = [f for f in REQUIRED_FIELDS if f not in fm]
    assert not missing, f"{skill_file}: Missing required fields: {missing}"


@pytest.mark.parametrize("skill_file", skill_files(), ids=lambda p: p.parent.name)
def test_name_matches_directory(skill_file: Path) -> None:
    fm = parse_frontmatter(skill_file)
    dir_name = skill_file.parent.name
    assert fm.get("name") == dir_name, (
        f"{skill_file}: name '{fm.get('name')}' does not match directory '{dir_name}'"
    )


@pytest.mark.parametrize("skill_file", skill_files(), ids=lambda p: p.parent.name)
def test_triggers_non_empty(skill_file: Path) -> None:
    fm = parse_frontmatter(skill_file)
    triggers = fm.get("triggers", [])
    assert isinstance(triggers, list) and len(triggers) > 0, (
        f"{skill_file}: 'triggers' must be a non-empty list"
    )


@pytest.mark.parametrize("skill_file", skill_files(), ids=lambda p: p.parent.name)
def test_required_scopes_is_list(skill_file: Path) -> None:
    fm = parse_frontmatter(skill_file)
    scopes = fm.get("required_scopes")
    assert isinstance(scopes, list), (
        f"{skill_file}: 'required_scopes' must be a list (can be empty [])"
    )


@pytest.mark.parametrize("skill_file", skill_files(), ids=lambda p: p.parent.name)
def test_references_directory_exists(skill_file: Path) -> None:
    refs = skill_file.parent / "references"
    assert refs.is_dir(), f"{skill_file.parent.name}: Missing references/ directory"


@pytest.mark.parametrize("skill_file", skill_files(), ids=lambda p: p.parent.name)
def test_version_is_string_or_number(skill_file: Path) -> None:
    fm = parse_frontmatter(skill_file)
    version = fm.get("version")
    assert version is not None, f"{skill_file}: 'version' is required"
    assert isinstance(version, (str, int, float)), (
        f"{skill_file}: 'version' must be a string or number"
    )


@pytest.mark.parametrize("skill_file", skill_files(), ids=lambda p: p.parent.name)
def test_description_non_empty(skill_file: Path) -> None:
    fm = parse_frontmatter(skill_file)
    desc = fm.get("description", "").strip()
    assert len(desc) > 20, (
        f"{skill_file}: 'description' must be a meaningful string (>20 chars)"
    )
