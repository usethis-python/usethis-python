"""Check that AGENTS.md and all SKILL.md files do not exceed the line limit.

Scans the AGENTS.md file and all SKILL.md files in the skills directory to
ensure no file exceeds the maximum number of lines. When a violation is found,
instructions are printed explaining how to reduce the file size.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that agent files do not exceed the line limit.",
    )
    parser.add_argument(
        "--agents-file",
        required=True,
        help="Path to the AGENTS.md file.",
    )
    parser.add_argument(
        "--skills-dir",
        required=True,
        help="Path to the skills directory containing subdirectories with SKILL.md files.",
    )
    parser.add_argument(
        "--max-lines",
        type=int,
        default=500,
        help="Maximum number of lines allowed per file (default: 500).",
    )
    args = parser.parse_args()

    agents_file = Path(args.agents_file)
    skills_dir = Path(args.skills_dir)
    max_lines: int = args.max_lines

    if not agents_file.is_file():
        print(f"ERROR: {agents_file} not found.")
        return 1

    if not skills_dir.is_dir():
        print(f"ERROR: {skills_dir} is not a directory.")
        return 1

    violations: list[tuple[Path, int]] = []

    agents_line_count = _count_lines(agents_file)
    if agents_line_count > max_lines:
        violations.append((agents_file, agents_line_count))

    for skill_file in sorted(skills_dir.glob("*/SKILL.md")):
        line_count = _count_lines(skill_file)
        if line_count > max_lines:
            violations.append((skill_file, line_count))

    if violations:
        print(f"ERROR: The following agent files exceed the {max_lines}-line limit:")
        for path, count in violations:
            print(f"  {path}: {count} lines (limit: {max_lines})")
        print()
        print("To fix these violations:")
        print(
            "  - For SKILL.md files: split the skill into sub-skills, each in its own"
            " subdirectory under .agents/skills/."
        )
        print(
            "  - For AGENTS.md: move general instructions into separate files referenced"
            " from AGENTS.md."
        )
        return 1

    return 0


def _count_lines(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


if __name__ == "__main__":
    raise SystemExit(main())
