#!/usr/bin/env python3
"""Validate all SKILL.md files conform to the plugin contract.

Exit 0: all skills valid.
Exit 1: one or more violations found.
"""
import sys
import yaml
from pathlib import Path

REQUIRED_FIELDS = ["name", "description", "version", "triggers", "required_scopes"]
SKILLS_DIR = Path(__file__).parent.parent / "skills"


def validate_skill(skill_path: Path) -> list[str]:
    errors = []
    content = skill_path.read_text()

    if not content.startswith("---"):
        return [f"{skill_path}: Missing YAML frontmatter (file must start with ---)"]

    parts = content.split("---", 2)
    if len(parts) < 3:
        return [f"{skill_path}: Malformed frontmatter (missing closing ---)"]

    try:
        fm = yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        return [f"{skill_path}: YAML parse error: {e}"]

    if not isinstance(fm, dict):
        return [f"{skill_path}: Frontmatter must be a YAML mapping"]

    for field in REQUIRED_FIELDS:
        if field not in fm:
            errors.append(f"{skill_path}: Missing required field '{field}'")

    dir_name = skill_path.parent.name
    if fm.get("name") and fm["name"] != dir_name:
        errors.append(
            f"{skill_path}: name '{fm['name']}' does not match directory '{dir_name}'"
        )

    refs_dir = skill_path.parent / "references"
    if not refs_dir.is_dir():
        errors.append(f"{skill_path.parent}: Missing references/ directory")

    if not isinstance(fm.get("triggers"), list) or not fm["triggers"]:
        errors.append(f"{skill_path}: 'triggers' must be a non-empty list")

    if not isinstance(fm.get("required_scopes"), list):
        errors.append(f"{skill_path}: 'required_scopes' must be a list (can be empty)")

    return errors


def main():
    if not SKILLS_DIR.is_dir():
        print(f"ERROR: skills/ directory not found at {SKILLS_DIR}", file=sys.stderr)
        sys.exit(1)

    skill_files = sorted(SKILLS_DIR.glob("*/SKILL.md"))
    if not skill_files:
        print("WARNING: No SKILL.md files found")
        sys.exit(0)

    all_errors: list[str] = []
    for skill_file in skill_files:
        errors = validate_skill(skill_file)
        all_errors.extend(errors)
        status = "FAIL" if errors else "OK  "
        print(f"{status}  {skill_file.parent.name}")
        for e in errors:
            print(f"      {e}")

    print()
    if all_errors:
        print(f"{len(all_errors)} error(s) — fix before committing", file=sys.stderr)
        sys.exit(1)

    print(f"{len(skill_files)} skill(s) validated OK")


if __name__ == "__main__":
    main()
