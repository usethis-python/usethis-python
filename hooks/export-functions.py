"""Export module-level functions with docstrings from a Python package.

Recursively scans all Python source files under a package root directory for
module-level functions with docstrings and writes a flat markdown bullet list
to an output file. Functions are listed in the order they appear in each file,
with files processed in sorted order. Class methods and nested functions are
not included. Functions without a docstring are skipped unless --strict is
used, in which case the script exits non-zero when any are found.

By default, private functions (those whose names start with an underscore) are
included. Pass --skip-private to exclude them.
"""

from __future__ import annotations

import argparse
import ast
import os
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export public function reference from a Python package.",
    )
    parser.add_argument(
        "--output-file",
        required=True,
        help="Path to the output file to write.",
    )
    parser.add_argument(
        "--source-root",
        required=True,
        help="Root package directory to scan for public functions.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Fail if any public module-level function lacks a docstring.",
    )
    parser.add_argument(
        "--skip-private",
        action="store_true",
        default=False,
        help="Exclude functions whose names start with an underscore.",
    )
    args = parser.parse_args()

    output_file = Path(args.output_file)
    source_root = Path(args.source_root)

    if not source_root.is_dir():
        print(f"ERROR: Source root {source_root} is not a directory.", file=sys.stderr)
        return 1

    bullets: list[str] = []
    missing: list[tuple[Path, str]] = []

    for py_file in _collect_py_files(source_root):
        try:
            module = _module_name(py_file, source_root)
        except ValueError:
            print(
                f"ERROR: {py_file} is not relative to source root {source_root}.",
                file=sys.stderr,
            )
            return 1

        for func_name, first_line in _get_module_public_functions(
            py_file, skip_private=args.skip_private
        ):
            if first_line is not None:
                bullets.append(f"- `{func_name}()` (`{module}`) — {first_line}")
            elif not func_name.startswith("_"):
                # Only track missing docstrings for public functions; private
                # functions without a docstring are silently omitted from output.
                missing.append((py_file, func_name))

    content = os.linesep.join(bullets) + os.linesep

    try:
        with open(output_file, encoding="utf-8", newline="") as f:
            existing = f.read()
    except FileNotFoundError:
        existing = None

    modified = content != existing
    if modified:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(content, encoding="utf-8", newline="")
        print(f"Function reference written to {output_file}.")
    else:
        print("Function reference is already up to date.")

    if args.strict and missing:
        print(
            f"ERROR: {len(missing)} public function(s) missing a docstring:",
            file=sys.stderr,
        )
        for path, name in missing:
            print(f"  - {path}:{name}", file=sys.stderr)
        return 1

    return 1 if modified else 0


def _module_name(source_file: Path, source_root: Path) -> str:
    """Derive a dotted module name from a file path, including the package name."""
    # Use source_root.parent so the package directory name itself is part of the path.
    rel = source_file.relative_to(source_root.parent)
    parts = rel.with_suffix("").parts
    # Drop __init__ from the tail so the module name matches the package path.
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _get_module_public_functions(
    path: Path, *, skip_private: bool = False
) -> list[tuple[str, str | None]]:
    """Return (name, docstring_first_line_or_None) for each top-level function.

    Only direct children of the module node are included (no class methods or
    nested functions). Functions are returned in source order. When skip_private
    is True, functions whose names start with an underscore are excluded.
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

    results: list[tuple[str, str | None]] = []
    for node in ast.iter_child_nodes(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if _is_overload(node):
            continue
        if skip_private and node.name.startswith("_"):
            continue
        docstring = ast.get_docstring(node)
        if docstring is not None:
            first_line = docstring.split("\n")[0].strip()
            # Normalize RST-style double backticks to markdown single backticks
            # so the output is compatible with prettier's markdown formatting.
            first_line = first_line.replace("``", "`")
            results.append((node.name, first_line if first_line else None))
        else:
            results.append((node.name, None))

    return results


def _is_overload(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Return True if the function is decorated with `@overload`."""
    return any(
        (isinstance(d, ast.Name) and d.id == "overload")
        or (isinstance(d, ast.Attribute) and d.attr == "overload")
        for d in node.decorator_list
    )


def _collect_py_files(source_root: Path) -> list[Path]:
    """Return all .py files under source_root in sorted order."""
    return sorted(source_root.rglob("*.py"))


if __name__ == "__main__":
    raise SystemExit(main())
