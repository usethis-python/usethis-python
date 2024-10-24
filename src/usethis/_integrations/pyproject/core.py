from typing import Any

import mergedeep

from usethis._integrations.pyproject.io import (
    read_pyproject_toml,
    write_pyproject_toml,
)


class ConfigValueAlreadySetError(ValueError):
    """Raised when a value is unexpectedly already set in the configuration file."""


class ConfigValueMissingError(ValueError):
    """Raised when a value is unexpectedly missing from the configuration file."""


def get_config_value(id_keys: list[str]) -> Any:
    pyproject = read_pyproject_toml()

    p = pyproject
    for key in id_keys:
        p = p[key]

    return p


def set_config_value(
    id_keys: list[str], value: Any, *, exists_ok: bool = False
) -> None:
    """Set a value in the pyproject.toml configuration file.

    Raises:
        ConfigValueAlreadySetError: If the configuration value is already set.
    """
    pyproject = read_pyproject_toml()

    try:
        p = pyproject
        for key in id_keys:
            p, parent = p[key], p
    except KeyError:
        # The old configuration should be kept for all ID keys except the
        # final/deepest one which shouldn't exist anyway since we checked as much,
        # above. For example, if there is [tool.ruff] then we shouldn't overwrite it
        # with [tool.deptry]; they should coexist. So under the "tool" key, we need
        # to merge the two dicts.
        contents = value
        for key in reversed(id_keys):
            contents = {key: contents}
        pyproject = mergedeep.merge(pyproject, contents)
    else:
        if not exists_ok:
            # The configuration is already present, which is not allowed.
            msg = f"Configuration value [{'.'.join(id_keys)}] is already set."
            raise ConfigValueAlreadySetError(msg)
        else:
            # The configuration is already present, but we're allowed to overwrite it.
            parent[id_keys[-1]] = value

    write_pyproject_toml(pyproject)


def remove_config_value(id_keys: list[str], *, missing_ok: bool = False) -> None:
    pyproject = read_pyproject_toml()

    # Exit early if the configuration is not present.
    try:
        p = pyproject
        for key in id_keys:
            p = p[key]
    except KeyError:
        if not missing_ok:
            # The configuration is not present, which is not allowed.
            raise ConfigValueMissingError(
                f"Configuration value [{'.'.join(id_keys)}] is missing."
            )
        else:
            # The configuration is not present, but that's okay; nothing left to do.
            return

    # Remove the configuration.
    p = pyproject
    for key in id_keys[:-1]:
        p = p[key]
    del p[id_keys[-1]]

    # Cleanup: any empty sections should be removed.
    for idx in range(len(id_keys) - 1):
        p = pyproject
        for key in id_keys[: idx + 1]:
            p, parent = p[key], p
        if not p:
            del parent[id_keys[idx]]

    write_pyproject_toml(pyproject)


def append_config_list(
    id_keys: list[str],
    values: list[Any],
) -> list[str]:
    """Append values to a list in the pyproject.toml configuration file."""
    pyproject = read_pyproject_toml()

    try:
        p = pyproject
        for key in id_keys[:-1]:
            p = p[key]
        p_parent = p
        p = p_parent[id_keys[-1]]
    except KeyError:
        contents = values
        for key in reversed(id_keys):
            contents = {key: contents}
        pyproject = mergedeep.merge(pyproject, contents)
    else:
        p_parent[id_keys[-1]] = p + values

    write_pyproject_toml(pyproject)


def remove_from_config_list(id_keys: list[str], values: list[str]) -> None:
    pyproject = read_pyproject_toml()

    try:
        p = pyproject
        for key in id_keys[:-1]:
            p = p[key]
        p_parent = p
        p = p_parent[id_keys[-1]]
    except KeyError:
        # The configuration is not present.
        return

    # Remove the rules from the existing configuration.
    new_values = [value for value in p if value not in values]
    p_parent[id_keys[-1]] = new_values

    write_pyproject_toml(pyproject)
