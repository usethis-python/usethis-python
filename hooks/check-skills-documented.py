"""Check that all skills in .agents/skills/ are mentioned in AGENTS.md."""

from __future__ import annotations

import sys
from pathlib import Path

AGENTS_MD = Path("AGENTS.md")
SKILLS_DIR = Path(".agents/skills")


def main() -> int:
    if not AGENTS_MD.is_file():
        print(f"ERROR: {AGENTS_MD} not found.", file=sys.stderr)
        return 1

    if not SKILLS_DIR.is_dir():
        print(f"ERROR: {SKILLS_DIR} directory not found.", file=sys.stderr)
        return 1

    agents_md_content = AGENTS_MD.read_text()

    missing = [
        d.name
        for d in sorted(SKILLS_DIR.iterdir())
        if d.is_dir() and d.name not in agents_md_content
    ]

    if missing:
        print(
            "ERROR: The following skills are not mentioned in AGENTS.md:",
            file=sys.stderr,
        )
        for skill in missing:
            print(f"  - {skill}", file=sys.stderr)
        print(file=sys.stderr)
        print("Please add them to the skills registry in AGENTS.md.", file=sys.stderr)
        return 1

    print("All skills are documented in AGENTS.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
