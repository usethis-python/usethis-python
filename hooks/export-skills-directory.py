"""Export a skills directory from SKILL.md YAML frontmatter.

Scans agent skill directories for SKILL.md files, extracts the name and
description from each file's YAML frontmatter, and writes a formatted
Markdown table to an output file.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def _parse_frontmatter(path: Path) -> dict[str, str]:
    """Extract top-level string fields from YAML frontmatter."""
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}
    frontmatter = match.group(1)
    fields: dict[str, str] = {}
    for line in frontmatter.splitlines():
        m = re.match(r"^(\w[\w-]*)\s*:\s*(.+)$", line)
        if m:
            key = m.group(1).strip()
            value = m.group(2).strip().strip('"').strip("'")
            fields[key] = value
    return fields


def main() -> int:
    """Export a skills directory table from SKILL.md frontmatter."""
    parser = argparse.ArgumentParser(
        description="Export a skills directory from SKILL.md frontmatter.",
    )
    parser.add_argument(
        "--skills-dir",
        required=True,
        help="Path to the skills directory to scan.",
    )
    parser.add_argument(
        "--output-file",
        required=True,
        help="Path to the output file to write the directory table to.",
    )
    parser.add_argument(
        "--prefix",
        default="usethis-",
        help="Only include skills whose directory name starts with this prefix.",
    )
    args = parser.parse_args()

    skills_dir = Path(args.skills_dir)
    output_file = Path(args.output_file)
    prefix: str = args.prefix

    if not skills_dir.is_dir():
        print(f"ERROR: {skills_dir} is not a directory.", file=sys.stderr)
        return 1

    rows: list[tuple[str, str]] = []
    missing: list[str] = []

    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        if not skill_dir.name.startswith(prefix):
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            missing.append(skill_dir.name)
            continue
        fields = _parse_frontmatter(skill_md)
        name = fields.get("name", skill_dir.name)
        description = fields.get("description", "")
        if not description:
            missing.append(skill_dir.name)
            continue
        rows.append((name, description))

    if not rows:
        print("ERROR: No skills found.", file=sys.stderr)
        return 1

    name_width = max(len(f"`{name}`") for name, _ in rows)
    desc_width = max(len(desc) for _, desc in rows)
    name_width = max(name_width, len("Skill"))
    desc_width = max(desc_width, len("Description"))

    lines: list[str] = []
    lines.append(f"| {'Skill':<{name_width}} | {'Description':<{desc_width}} |")
    lines.append(f"| {'-' * name_width} | {'-' * desc_width} |")
    for name, desc in rows:
        formatted_name = f"`{name}`"
        lines.append(f"| {formatted_name:<{name_width}} | {desc:<{desc_width}} |")

    content = "\n".join(lines) + "\n"

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(content, encoding="utf-8")

    print(f"Skills directory written to {output_file}.")

    if missing:
        print(
            f"WARNING: {len(missing)} skill(s) missing SKILL.md or description:",
            file=sys.stderr,
        )
        for name in missing:
            print(f"  - {name}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
