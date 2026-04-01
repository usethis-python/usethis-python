"""Check that hook scripts do not contain banned words.

Scans all Python files in the hooks directory for occurrences of words that
should not appear. This enforces generality in hooks by preventing them from
referencing project-specific names. The banned words are provided as
positional command-line arguments.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that hook scripts do not contain banned words.",
    )
    parser.add_argument(
        "--hooks-dir",
        required=True,
        help="Path to the hooks directory to scan.",
    )
    parser.add_argument(
        "words",
        nargs="+",
        help="Words to ban from hook scripts.",
    )
    args = parser.parse_args()

    hooks_dir = Path(args.hooks_dir)
    banned: list[str] = args.words
    own_name = Path(__file__).name

    if not hooks_dir.is_dir():
        print(f"ERROR: {hooks_dir} is not a directory.", file=sys.stderr)
        return 1

    violations: list[str] = []
    patterns = [
        re.compile(r"\b" + re.escape(word) + r"\b", re.IGNORECASE) for word in banned
    ]
    for py_file in sorted(hooks_dir.glob("*.py")):
        if py_file.name == own_name:
            continue
        lines = py_file.read_text(encoding="utf-8").splitlines()
        for lineno, line in enumerate(lines, start=1):
            for pattern in patterns:
                if pattern.search(line):
                    violations.append(f"  {py_file}:{lineno}: {line.strip()}")

    if violations:
        print(
            "ERROR: Banned word(s) found in hook scripts:",
            file=sys.stderr,
        )
        for v in violations:
            print(v, file=sys.stderr)
        return 1

    print("No banned words found in hook scripts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
