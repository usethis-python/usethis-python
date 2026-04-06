"""Check that docstrings do not contain forbidden patterns.

Parses Python files using the AST module and checks only docstring content
against one or more forbidden regex patterns. Reports file, line, and column
of each violation.
"""

from __future__ import annotations

import argparse
import ast
import re
import sys


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that docstrings do not contain forbidden patterns.",
    )
    parser.add_argument(
        "--pattern",
        action="append",
        required=True,
        dest="patterns",
        help="Regex pattern to forbid in docstrings. Can be repeated.",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Python files to check.",
    )
    args = parser.parse_args()

    compiled = [re.compile(p) for p in args.patterns]
    violations: list[str] = []

    for filepath in args.files:
        violations.extend(_check_file(filepath, compiled))

    if violations:
        print("ERROR: Forbidden pattern(s) found in docstrings:", file=sys.stderr)
        for v in violations:
            print(v, file=sys.stderr)
        return 1

    print("No forbidden patterns found in docstrings.")
    return 0


def _check_file(filepath: str, patterns: list[re.Pattern[str]]) -> list[str]:
    try:
        with open(filepath, encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source, filename=filepath)
    except (SyntaxError, UnicodeDecodeError):
        return []

    violations: list[str] = []
    for node in _iter_docstring_nodes(tree):
        docstring = node.value
        assert isinstance(docstring, str)
        lines = docstring.split("\n")
        for i, line in enumerate(lines):
            for pattern in patterns:
                for match in pattern.finditer(line):
                    file_lineno = node.lineno + i
                    col = match.start()
                    violations.append(
                        f"  {filepath}:{file_lineno}:{col}: {line.strip()}"
                    )
    return violations


def _iter_docstring_nodes(tree: ast.AST) -> list[ast.Constant]:
    nodes: list[ast.Constant] = []
    for node in ast.walk(tree):
        if isinstance(
            node,
            (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef),
        ):
            _collect_docstring(node, nodes)
    return nodes


def _collect_docstring(
    node: ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef,
    out: list[ast.Constant],
) -> None:
    if (
        node.body
        and isinstance(node.body[0], ast.Expr)
        and isinstance(node.body[0].value, ast.Constant)
        and isinstance(node.body[0].value.value, str)
    ):
        out.append(node.body[0].value)


if __name__ == "__main__":
    raise SystemExit(main())
