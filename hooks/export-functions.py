"""Export important utility functions with docstrings to a markdown reference file.

Scans specified Python source files for public functions with docstrings and
writes a flat markdown reference to an output file.  Only functions with a
docstring are included; undocumented functions are skipped.  Functions are
listed in the order they appear in each module, and modules are listed in the
order they appear in MODULES.
"""

from __future__ import annotations

import argparse
import ast
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class _Entry:
    module: str
    file: str


# The modules to scan for public functions with docstrings.
# Add entries here to include additional modules in the reference.
MODULES: list[_Entry] = [
    _Entry(module="usethis._deps", file="src/usethis/_deps.py"),
    _Entry(module="usethis._console", file="src/usethis/_console.py"),
    _Entry(
        module="usethis._detect.pre_commit",
        file="src/usethis/_detect/pre_commit.py",
    ),
    _Entry(
        module="usethis._detect.readme",
        file="src/usethis/_detect/readme.py",
    ),
    _Entry(
        module="usethis._integrations.project.build",
        file="src/usethis/_integrations/project/build.py",
    ),
    _Entry(
        module="usethis._integrations.project.name",
        file="src/usethis/_integrations/project/name.py",
    ),
    _Entry(
        module="usethis._integrations.project.packages",
        file="src/usethis/_integrations/project/packages.py",
    ),
    _Entry(
        module="usethis._integrations.project.layout",
        file="src/usethis/_integrations/project/layout.py",
    ),
    _Entry(
        module="usethis._file.pyproject_toml.requires_python",
        file="src/usethis/_file/pyproject_toml/requires_python.py",
    ),
    _Entry(
        module="usethis._file.pyproject_toml.name",
        file="src/usethis/_file/pyproject_toml/name.py",
    ),
    _Entry(
        module="usethis._backend.dispatch",
        file="src/usethis/_backend/dispatch.py",
    ),
]


def _get_public_functions(path: Path) -> list[tuple[str, str]]:
    """Return (name, first_docstring_line) for each public function in the file.

    Functions without a docstring are excluded.
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
        description="Export utility function reference to a markdown file.",
    )
    parser.add_argument(
        "--output-file",
        required=True,
        help="Path to the output markdown file to write.",
    )
    args = parser.parse_args()

    output_file = Path(args.output_file)

    bullets: list[str] = []
    failed = False

    for entry in MODULES:
        source_path = Path(entry.file)
        if not source_path.is_file():
            print(
                f"ERROR: Source file {source_path} not found.",
                file=sys.stderr,
            )
            failed = True
            continue

        for func_name, first_line in _get_public_functions(source_path):
            bullets.append(f"- `{func_name}()` (`{entry.module}`) — {first_line}")

    content = "\n".join(bullets) + "\n"

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(content, encoding="utf-8")

    print(f"Function reference written to {output_file}.")

    if failed:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
