"""Check that priority groups in a pre-commit config file are monotone.

Reads a YAML configuration file (e.g. `.pre-commit-config.yaml`) and extracts
the `priority` field from each hook entry. Verifies that the sequence of
priority values is non-decreasing (monotone), meaning hooks in the same priority
group are adjacent and groups appear in ascending order.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that priority groups in a pre-commit config are monotone.",
    )
    parser.add_argument(
        "--config-file",
        required=True,
        help="Path to the pre-commit configuration YAML file.",
    )
    args = parser.parse_args()

    config_path = Path(args.config_file)

    if not config_path.is_file():
        print(f"ERROR: {config_path} not found.", file=sys.stderr)
        return 1

    priorities = _extract_priorities(config_path)

    if not priorities:
        print(f"No priority fields found in {config_path}.")
        return 0

    violations = _find_violations(priorities)

    if violations:
        print(
            f"ERROR: Priority groups in {config_path} are not monotone.",
            file=sys.stderr,
        )
        for prev_line, prev_val, cur_line, cur_val in violations:
            print(
                f"  Line {cur_line}: priority {cur_val} follows "
                f"priority {prev_val} (line {prev_line})",
                file=sys.stderr,
            )
        return 1

    print(f"Priority groups in {config_path} are monotone.")
    return 0


def _extract_priorities(config_path: Path) -> list[tuple[int, int]]:
    """Extract (line_number, priority_value) pairs from the config file."""
    priority_pattern = re.compile(r"^\s+priority:\s+(\d+)\s*$")
    priorities: list[tuple[int, int]] = []

    text = config_path.read_text(encoding="utf-8")
    for lineno, line in enumerate(text.splitlines(), start=1):
        match = priority_pattern.match(line)
        if match:
            priorities.append((lineno, int(match.group(1))))

    return priorities


def _find_violations(
    priorities: list[tuple[int, int]],
) -> list[tuple[int, int, int, int]]:
    """Find pairs where priority decreases.

    Returns a list of (prev_line, prev_value, cur_line, cur_value) tuples
    for each violation.
    """
    violations: list[tuple[int, int, int, int]] = []
    for i in range(1, len(priorities)):
        prev_line, prev_val = priorities[i - 1]
        cur_line, cur_val = priorities[i]
        if cur_val < prev_val:
            violations.append((prev_line, prev_val, cur_line, cur_val))
    return violations


if __name__ == "__main__":
    raise SystemExit(main())
