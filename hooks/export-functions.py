"""Export all functions with docstrings from a package to a markdown reference file.

Recursively scans a Python package directory for all functions (including
private ones) and writes a flat markdown bullet list to an output file.
Functions are listed in the order they appear in each module; modules are
visited in sorted order.  Pass ``--strict`` to fail when any function is
missing a docstring.
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path


def _path_to_module(path: Path, source_root: Path) -> str:
    """Convert a .py file path to a dotted module name.

    The module name is derived relative to the parent of source_root, so that
    the package name itself is included (e.g. ``src/pkg/sub/mod.py`` with
    ``source_root=src/pkg`` gives ``pkg.sub.mod``).
    """
    rel = path.relative_to(source_root.parent)
    parts = list(rel.with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _collect_py_files(source_root: Path) -> list[Path]:
    """Return all .py files under source_root in sorted order."""
    return sorted(source_root.rglob("*.py"))


def _get_functions(path: Path) -> list[tuple[str, str | None]]:
    """Return (name, docstring_first_line_or_None) for every function in path."""
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

    results: list[tuple[str, str | None]] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        docstring = ast.get_docstring(node)
        if docstring is not None:
            first_line = docstring.split("\n")[0].strip()
            results.append((node.name, first_line if first_line else None))
        else:
            results.append((node.name, None))

    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export a function reference from a Python package to a markdown file.",
    )
    parser.add_argument(
        "--source-root",
        required=True,
        help="Path to the root package directory to scan.",
    )
    parser.add_argument(
        "--output-file",
        required=True,
        help="Path to the output markdown file to write.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Fail if any function is missing a docstring.",
    )
    args = parser.parse_args()

    source_root = Path(args.source_root)
    output_file = Path(args.output_file)

    if not source_root.is_dir():
        print(f"ERROR: Source root {source_root} is not a directory.", file=sys.stderr)
        return 1

    if not (source_root / "__init__.py").is_file():
        print(
            f"ERROR: {source_root} is not a Python package (no __init__.py).",
            file=sys.stderr,
        )
        return 1

    bullets: list[str] = []
    missing: list[tuple[Path, str]] = []

    for py_file in _collect_py_files(source_root):
        module = _path_to_module(py_file, source_root)
        for func_name, first_line in _get_functions(py_file):
            if first_line is not None:
                bullets.append(f"- `{func_name}()` (`{module}`) — {first_line}")
            else:
                missing.append((py_file, func_name))
                bullets.append(f"- `{func_name}()` (`{module}`)")

    content = "\n".join(bullets) + "\n"

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(content, encoding="utf-8")

    print(f"Function reference written to {output_file}.")

    if args.strict and missing:
        print(
            f"ERROR: {len(missing)} function(s) missing a docstring:",
            file=sys.stderr,
        )
        for path, name in missing:
            print(f"  - {name} in {path}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
