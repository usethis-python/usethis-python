"""Export the supported configuration files for each managed tool.

Reads all usethis tool specifications and writes the list of supported
configuration files (in priority order) to an output file. The output can be
compared against documentation to verify it is up to date.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from unittest.mock import patch

from usethis._config_file import files_manager
from usethis._tool.impl.spec.all_ import ALL_TOOL_SPECS


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export supported config files per tool.",
    )
    parser.add_argument(
        "--output-file",
        required=True,
        help="Path to the output file to write.",
    )
    args = parser.parse_args()

    output_file = Path(args.output_file)
    lines = _build_lines()
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


def _build_lines() -> list[str]:
    lines = []
    with files_manager():
        for spec in ALL_TOOL_SPECS:
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


_DEFAULT_RESOLUTION = "first"


def _get_paths_and_resolution(spec: object) -> tuple[list[Path], str | None]:
    # Some specs expose a static file manager accessor to avoid expensive analysis
    # (e.g. an import graph build). Use it if available.
    get_fmbr = getattr(spec, "_get_file_manager_by_relative_path", None)
    if get_fmbr is not None:
        paths = list(get_fmbr().keys())
        get_res = getattr(spec, "_get_resolution", None)
        resolution: str | None = (
            get_res() if get_res is not None else _DEFAULT_RESOLUTION
        )
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
        except (AssertionError, NotImplementedError):
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
