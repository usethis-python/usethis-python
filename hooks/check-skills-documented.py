"""Check that all skills are documented in AGENTS.md.

Two checks are performed:
1. Skills in .agents/skills/ that start with 'usethis-' must appear in AGENTS.md.
2. External skills in skills-lock.json (those not starting with 'usethis-') must
   appear in AGENTS.md.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

AGENTS_MD = Path("AGENTS.md")
SKILLS_DIR = Path(".agents/skills")
SKILLS_LOCK = Path("skills-lock.json")
USETHIS_PREFIX = "usethis-"


def main() -> int:
    if not AGENTS_MD.is_file():
        print(f"ERROR: {AGENTS_MD} not found.", file=sys.stderr)
        return 1

    if not SKILLS_DIR.is_dir():
        print(f"ERROR: {SKILLS_DIR} directory not found.", file=sys.stderr)
        return 1

    if not SKILLS_LOCK.is_file():
        print(f"ERROR: {SKILLS_LOCK} not found.", file=sys.stderr)
        return 1

    agents_md_content = AGENTS_MD.read_text(encoding="utf-8")
    failed = False

    # Check 1: usethis- skills in the skills directory must be documented.
    usethis_skills = [
        d.name
        for d in sorted(SKILLS_DIR.iterdir())
        if d.is_dir() and d.name.startswith(USETHIS_PREFIX)
    ]
    undocumented_local = [
        name for name in usethis_skills if name not in agents_md_content
    ]
    if undocumented_local:
        print(
            f"ERROR: The following skills in {SKILLS_DIR} are not documented in {AGENTS_MD}:",
            file=sys.stderr,
        )
        for skill in undocumented_local:
            print(f"  - {skill}", file=sys.stderr)
        print(file=sys.stderr)
        print("Please add them to the skills registry in AGENTS.md.", file=sys.stderr)
        failed = True

    # Check 2: external skills in skills-lock.json must be documented.
    data = json.loads(SKILLS_LOCK.read_text(encoding="utf-8"))
    external_skills = [
        name
        for name in sorted(data.get("skills", {}).keys())
        if not name.startswith(USETHIS_PREFIX)
    ]
    undocumented_external = [
        name for name in external_skills if name not in agents_md_content
    ]
    if undocumented_external:
        if failed:
            print(file=sys.stderr)
        print(
            f"ERROR: The following external skills in {SKILLS_LOCK} are not documented in {AGENTS_MD}:",
            file=sys.stderr,
        )
        for skill in undocumented_external:
            print(f"  - {skill}", file=sys.stderr)
        print(file=sys.stderr)
        print(
            "Please add them to the external skills registry in AGENTS.md.",
            file=sys.stderr,
        )
        failed = True

    if failed:
        return 1

    print("All skills are documented in AGENTS.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
