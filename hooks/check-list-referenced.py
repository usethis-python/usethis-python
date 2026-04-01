"""Check that all items from a Python list constant appear in a target file.

Imports a named variable from a Python module using a dotted path reference
(e.g. ``pkg.mod.VAR``), then verifies each string item appears in a target
file. Useful for ensuring that a registry of commands or tools stays in sync
with documentation.
"""

from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path


def _resolve_variable(dotted_path: str) -> list[str]:
    """Import and return a list of strings from a dotted module path.

    The *dotted_path* must be of the form ``module.path.ATTR_NAME``.  The
    last component is treated as an attribute on the imported module.

    Raises ``SystemExit`` with a descriptive message on failure.
    """
    parts = dotted_path.rsplit(".", 1)
    if len(parts) != 2:
        print(
            f"ERROR: '{dotted_path}' is not a valid dotted path "
            f"(expected module.path.ATTR_NAME).",
            file=sys.stderr,
        )
        raise SystemExit(1)
    module_path, attr_name = parts
    try:
        module = importlib.import_module(module_path)
    except ImportError:
        print(
            f"ERROR: Could not import module '{module_path}'.",
            file=sys.stderr,
        )
        raise SystemExit(1) from None
    value = getattr(module, attr_name, None)
    if value is None:
        print(
            f"ERROR: Module '{module_path}' has no attribute '{attr_name}'.",
            file=sys.stderr,
        )
        raise SystemExit(1)
    if not isinstance(value, list):
        print(
            f"ERROR: '{dotted_path}' is not a list (got {type(value).__name__}).",
            file=sys.stderr,
        )
        raise SystemExit(1)
    return [item for item in value if isinstance(item, str)]


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that all items from a Python list constant appear in a target file."
        ),
    )
    parser.add_argument(
        "--variable",
        required=True,
        help="Dotted path to the list variable (e.g. pkg.mod.VAR_NAME).",
    )
    parser.add_argument(
        "--target-file",
        required=True,
        help="Path to the file that should reference every item.",
    )
    args = parser.parse_args()

    target_path = Path(args.target_file)

    if not target_path.is_file():
        print(f"ERROR: {target_path} not found.", file=sys.stderr)
        return 1

    items = _resolve_variable(args.variable)

    target_content = target_path.read_text(encoding="utf-8")
    missing = [item for item in items if item not in target_content]

    if missing:
        print(
            f"ERROR: The following items from '{args.variable}' "
            f"are not referenced in {target_path}:",
            file=sys.stderr,
        )
        for item in missing:
            print(f"  - {item!r}", file=sys.stderr)
        return 1

    print(f"All items from '{args.variable}' are referenced in {target_path}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
