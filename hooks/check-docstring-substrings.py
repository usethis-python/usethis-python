"""Check that docstrings do not contain forbidden substrings.

Parses Python files using the ast module and checks only docstring content
(not code or comments) for substrings that should not appear. The forbidden
substrings are provided via --forbidden arguments.
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that docstrings do not contain forbidden substrings.",
    )
    parser.add_argument(
        "--forbidden",
        action="append",
        required=True,
        help="Substring to forbid in docstrings. Can be repeated.",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Python files to check.",
    )
    args = parser.parse_args()

    forbidden: list[str] = args.forbidden
    files: list[str] = args.files

    if not files:
        print("No files to check.")
        return 0

    violations: list[str] = []
    for filepath in files:
        violations.extend(_check_file(filepath, forbidden))

    if violations:
        print(
            "ERROR: Forbidden substring(s) found in docstrings:",
            file=sys.stderr,
        )
        for v in violations:
            print(v, file=sys.stderr)
        return 1

    print(
        f"No forbidden substrings found in docstrings ({len(files)} file(s) checked)."
    )
    return 0


def _check_file(filepath: str, forbidden: list[str]) -> list[str]:
    """Check a single file for forbidden substrings in docstrings."""
    try:
        source = Path(filepath).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []

    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError:
        return []

    violations: list[str] = []
    for node in _docstring_nodes(tree):
        violations.extend(_check_docstring_node(filepath, source, node, forbidden))
    return violations


def _docstring_nodes(tree: ast.Module) -> list[ast.Constant]:
    """Collect all AST nodes that represent docstrings."""
    _HAS_BODY = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
    nodes: list[ast.Constant] = []
    for node in ast.walk(tree):
        if isinstance(node, _HAS_BODY) and node.body:
            first = node.body[0]
            if (
                isinstance(first, ast.Expr)
                and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)
            ):
                nodes.append(first.value)
    return nodes


def _check_docstring_node(
    filepath: str,
    source: str,
    node: ast.Constant,
    forbidden: list[str],
) -> list[str]:
    """Check a single docstring node for forbidden substrings."""
    violations: list[str] = []
    if not isinstance(node.value, str):
        return violations
    docstring: str = node.value
    source_lines = source.splitlines()
    start_line = node.lineno  # 1-based

    for line_offset, doc_line in enumerate(docstring.splitlines()):
        for substr in forbidden:
            col = doc_line.find(substr)
            if col == -1:
                continue
            abs_line = start_line + line_offset
            # Get the actual source line for display
            if 1 <= abs_line <= len(source_lines):
                display = source_lines[abs_line - 1].strip()
            else:
                display = doc_line.strip()
            violations.append(f"  {filepath}:{abs_line}: {display}")
    return violations


if __name__ == "__main__":
    raise SystemExit(main())
