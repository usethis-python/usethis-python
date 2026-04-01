"""Check that all items from a Python list constant appear in a target file.

Parses a Python source file with AST to extract a named list of string
constants, then verifies each item appears in a target file when formatted
with a user-supplied pattern. Useful for ensuring that a registry of commands
or tools stays in sync with documentation.
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path


def _extract_string_list(source: str, variable: str) -> list[str] | None:
    """Extract a list of string constants assigned to *variable* in *source*.

    Handles both plain assignment (``x = [...]``) and annotated assignment
    (``x: list[str] = [...]``).
    """
    tree = ast.parse(source)
    for node in ast.walk(tree):
        value: ast.expr | None = None
        # Plain assignment: x = [...]
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == variable:
                    value = node.value
        # Annotated assignment: x: list[str] = [...]
        elif isinstance(node, ast.AnnAssign):
            target = node.target
            if isinstance(target, ast.Name) and target.id == variable:
                value = node.value
        if isinstance(value, ast.List):
            return [
                elt.value
                for elt in value.elts
                if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
            ]
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that all items from a Python list constant appear in a target file."
        ),
    )
    parser.add_argument(
        "--source-file",
        required=True,
        help="Path to the Python file containing the list constant.",
    )
    parser.add_argument(
        "--variable",
        required=True,
        help="Name of the list variable to extract.",
    )
    parser.add_argument(
        "--target-file",
        required=True,
        help="Path to the file that should reference every item.",
    )
    parser.add_argument(
        "--pattern",
        required=True,
        help="Pattern where '{}' is replaced with each item to form the expected text.",
    )
    args = parser.parse_args()

    source_path = Path(args.source_file)
    target_path = Path(args.target_file)

    if not source_path.is_file():
        print(f"ERROR: {source_path} not found.", file=sys.stderr)
        return 1

    if not target_path.is_file():
        print(f"ERROR: {target_path} not found.", file=sys.stderr)
        return 1

    items = _extract_string_list(source_path.read_text(encoding="utf-8"), args.variable)
    if items is None:
        print(
            f"ERROR: Could not find list variable '{args.variable}' in {source_path}.",
            file=sys.stderr,
        )
        return 1

    target_content = target_path.read_text(encoding="utf-8")
    pattern: str = args.pattern

    missing: list[str] = []
    for item in items:
        expected = pattern.replace("{}", item)
        if expected not in target_content:
            missing.append(item)

    if missing:
        print(
            f"ERROR: The following items from '{args.variable}' "
            f"are not referenced in {target_path}:",
            file=sys.stderr,
        )
        for item in missing:
            expected = pattern.replace("{}", item)
            print(f"  - {item!r} (expected {expected!r})", file=sys.stderr)
        return 1

    print(f"All items from '{args.variable}' are referenced in {target_path}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
