"""Export the supported configuration files for each managed tool.

Reads all tool specifications from a Python variable and writes the list of
supported configuration files (in priority order) to an output file. The output
can be compared against documentation to verify it is up to date.

Specs are loaded from --specs-variable (a dotted module.VARIABLE path). An
optional --context-manager (dotted module.function path) wraps the export in a
context, useful when tool specs need open file managers to resolve config paths.
"""

from __future__ import annotations

import argparse
import contextlib
import importlib
import os
from pathlib import Path
from unittest.mock import patch


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export supported config files per tool from a Python API.",
    )
    parser.add_argument(
        "--output-file",
        required=True,
        help="Path to the output file to write.",
    )
    parser.add_argument(
        "--specs-variable",
        required=True,
        help="Dotted path to the list of tool spec objects, e.g. 'pkg.module.VAR'.",
    )
    parser.add_argument(
        "--context-manager",
        default=None,
        help=(
            "Dotted path to a zero-argument context manager function, "
            "e.g. 'pkg.module.ctx'. Activated around the spec iteration."
        ),
    )
    args = parser.parse_args()

    output_file = Path(args.output_file)
    lines = _build_lines(args.specs_variable, args.context_manager)
    content = os.linesep.join(lines) + os.linesep

    try:
        with open(output_file, encoding="utf-8", newline="") as f:
            existing = f.read()
    except FileNotFoundError:
        existing = None

    modified = content != existing
    if modified:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(content, encoding="utf-8", newline="")
        print(f"Config file reference written to {output_file}.")
    else:
        print("Config file reference is already up to date.")

    return 1 if modified else 0


def _build_lines(specs_variable: str, context_manager_path: str | None) -> list[str]:
    module_path, _, attr = specs_variable.rpartition(".")
    all_specs = getattr(importlib.import_module(module_path), attr)
    cm = _load_context_manager(context_manager_path)

    lines = []
    with cm:
        for spec in all_specs:
            paths, resolution = _get_paths_and_resolution(spec)
            if not paths:
                continue
            files_str = ", ".join(str(p) for p in paths)
            name = getattr(spec, "name", str(spec))
            if resolution is not None:
                lines.append(f"{name}: {files_str} (resolution={resolution})")
            else:
                lines.append(f"{name}: {files_str}")

    return lines


def _load_context_manager(
    path: str | None,
) -> contextlib.AbstractContextManager[object]:
    if path is None:
        return contextlib.nullcontext()
    module_path, _, attr = path.rpartition(".")
    ctx_fn = getattr(importlib.import_module(module_path), attr)
    return ctx_fn()


def _get_paths_and_resolution(spec: object) -> tuple[list[Path], str | None]:
    # Some specs expose a static file manager accessor to avoid expensive analysis
    # (e.g. an import graph build). Use it if available.
    get_fmbr = getattr(spec, "_get_file_manager_by_relative_path", None)
    if get_fmbr is not None:
        paths = list(get_fmbr().keys())
        get_res = getattr(spec, "_get_resolution", None)
        resolution: str | None = get_res() if get_res is not None else "first"
        if paths:
            return paths, resolution

    # Patch out any expensive import graph analysis so that config_spec() returns
    # quickly with just the file manager mapping.
    with patch.object(
        spec,
        "_get_layered_architecture_by_module_by_root_package",
        return_value={},
        create=True,
    ):
        try:
            config_spec_fn = getattr(spec, "config_spec", None)
            config = config_spec_fn() if config_spec_fn is not None else None
        except Exception:
            config = None

    if config is not None:
        fmbr = getattr(config, "file_manager_by_relative_path", {})
        paths = list(fmbr.keys())
        if paths:
            return paths, getattr(config, "resolution", None)

    # Fall back to managed_files for tools that don't use a ConfigSpec.
    meta = getattr(spec, "meta", None)
    managed_files: list[Path] = list(getattr(meta, "managed_files", []))
    return managed_files, None


if __name__ == "__main__":
    raise SystemExit(main())
