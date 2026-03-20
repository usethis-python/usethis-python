from __future__ import annotations

from typing import TYPE_CHECKING

from usethis._console import warn_print
from usethis.errors import FileConfigError

if TYPE_CHECKING:
    from usethis._tool.spec import ToolSpec


def is_likely_used(tool_spec: ToolSpec) -> bool:
    """Determine whether a tool is likely used in the current project.

    Four heuristics are used:
    1. Whether any of the tool's managed files are present.
    2. Whether any of the tool's characteristic dependencies are declared.
    3. Whether any of the tool's managed config file sections are present.
    4. Whether any of the tool's characteristic pre-commit hooks are present.

    Args:
        tool_spec: The tool specification to check.

    Returns:
        True if the tool is likely used, False otherwise.
    """
    decode_err_by_name: dict[str, FileConfigError] = {}
    _is_used = False

    _is_used = any(file.exists() and file.is_file() for file in tool_spec.managed_files)

    if not _is_used:
        try:
            _is_used = tool_spec.is_declared_as_dep()
        except FileConfigError as err:
            decode_err_by_name[err.name] = err

    if not _is_used:
        try:
            _is_used = tool_spec.config_spec().is_present()
        except FileConfigError as err:
            decode_err_by_name[err.name] = err

    # Do this last since the YAML parsing is expensive.
    if not _is_used:
        try:
            _is_used = tool_spec.is_pre_commit_config_present()
        except FileConfigError as err:
            decode_err_by_name[err.name] = err

    for name, decode_err in decode_err_by_name.items():
        warn_print(decode_err)
        warn_print(
            f"Assuming '{name}' contains no evidence of {tool_spec.name} being used."
        )

    return _is_used
