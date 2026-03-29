"""Export public functions with docstrings from Python source files to a reference file.

Scans the specified Python source files for public functions with a docstring and
writes a flat markdown bullet list to an output file. Functions are listed in the
order they appear in the source files, which are processed in the order given on
the command line. Functions without a docstring are skipped.
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path


def _module_name(source_file: Path, source_root: Path) -> str:
    """Derive a dotted module name from a file path relative to the source root."""
    rel = source_file.relative_to(source_root)
    parts = rel.with_suffix("").parts
    return ".".join(parts)


def _get_public_functions(path: Path) -> list[tuple[str, str]]:
    """Return (name, first_docstring_line) for each public function in the file.

    Functions without a docstring are excluded. Functions are returned in source order.
    """
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"ERROR: Cannot read {path}: {exc}", file=sys.stderr)
        return []

    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        print(f"ERROR: Cannot parse {path}: {exc}", file=sys.stderr)
        return []

    results: list[tuple[str, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name.startswith("_"):
            continue
        docstring = ast.get_docstring(node)
        if docstring is None:
            continue
        first_line = docstring.split("\n")[0].strip()
        if first_line:
            results.append((node.name, first_line))

    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export public function reference to a markdown file.",
    )
    parser.add_argument(
        "--output-file",
        required=True,
        help="Path to the output file to write.",
    )
    parser.add_argument(
        "--source-root",
        required=True,
        help="Root directory used to derive dotted module names from file paths.",
    )
    parser.add_argument(
        "source_files",
        nargs="+",
        help="Python source files to scan for public functions.",
    )
    args = parser.parse_args()

    output_file = Path(args.output_file)
    source_root = Path(args.source_root)
    failed = False
    bullets: list[str] = []

    for source_file_str in args.source_files:
        source_path = Path(source_file_str)
        if not source_path.is_file():
            print(f"ERROR: Source file {source_path} not found.", file=sys.stderr)
            failed = True
            continue

        try:
            module = _module_name(source_path, source_root)
        except ValueError:
            print(
                f"ERROR: {source_path} is not relative to source root {source_root}.",
                file=sys.stderr,
            )
            failed = True
            continue

        for func_name, first_line in _get_public_functions(source_path):
            bullets.append(f"- `{func_name}()` (`{module}`) — {first_line}")

    content = "\n".join(bullets) + "\n"

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(content, encoding="utf-8")

    print(f"Function reference written to {output_file}.")

    if failed:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
