from pathlib import Path
from typing import Any, Literal, assert_never

import mergedeep
import tomlkit


class ConfigValueAlreadySetError(ValueError):
    """Raised when a value is unexpectedly already set in the configuration file."""


class ConfigValueMissingError(ValueError):
    """Raised when a value is unexpectedly missing from the configuration file."""


def get_config_value(id_keys: list[str]) -> Any:
    pyproject = tomlkit.parse((Path.cwd() / "pyproject.toml").read_text())

    p = pyproject
    for key in id_keys:
        p = p[key]

    return p


def set_config_value(id_keys: list[str], value: Any) -> None:
    """Set a value in the pyproject.toml configuration file.

    Raises:
        ConfigValueAlreadySetError: If the configuration value is already set.
    """
    pyproject = tomlkit.parse((Path.cwd() / "pyproject.toml").read_text())

    try:
        p = pyproject
        for key in id_keys:
            p = p[key]
    except KeyError:
        pass
    else:
        # The configuration is already present.
        msg = f"Configuration value [{'.'.join(id_keys)}] is already set."
        raise ConfigValueAlreadySetError(msg)

    # The old configuration should be kept for all ID keys except the
    # final/deepest one which shouldn't exist anyway since we checked as much,
    # above. For example, if there is [tool.ruff] then we shouldn't overwrite it
    # with [tool.deptry]; they should coexist. So under the "tool" key, we need
    # to merge the two dicts.
    contents = value
    for key in reversed(id_keys):
        contents = {key: contents}
    pyproject = mergedeep.merge(pyproject, contents)

    (Path.cwd() / "pyproject.toml").write_text(tomlkit.dumps(pyproject))


def remove_config_value(id_keys: list[str]) -> None:
    pyproject = tomlkit.parse((Path.cwd() / "pyproject.toml").read_text())

    # Exit early if the configuration is not present.
    try:
        p = pyproject
        for key in id_keys:
            p = p[key]
    except KeyError:
        # The configuration is not present.
        raise ConfigValueMissingError(
            f"Configuration value [{'.'.join(id_keys)}] is missing."
        )

    # Remove the configuration.
    p = pyproject
    for key in id_keys[:-1]:
        p = p[key]
    del p[id_keys[-1]]

    # Cleanup: any empty sections should be removed.
    for idx in range(len(id_keys) - 1):
        p = pyproject
        for key in id_keys[: idx + 1]:
            p = p[key]
        if not p:
            del p

    (Path.cwd() / "pyproject.toml").write_text(tomlkit.dumps(pyproject))


def append_config_list(
    id_keys: list[str],
    values: list[Any],
    *,
    order: Literal["sorted", "preserved"] = "sorted",
) -> list[str]:
    """Append values to a list in the pyproject.toml configuration file."""
    pyproject = tomlkit.parse((Path.cwd() / "pyproject.toml").read_text())

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
        # Append to the existing configuration.
        if order == "sorted":
            new_values = sorted(p + values)
        elif order == "preserved":
            new_values = p + values
        else:
            assert_never(order)

        p_parent[id_keys[-1]] = new_values

    (Path.cwd() / "pyproject.toml").write_text(tomlkit.dumps(pyproject))


def remove_from_config_list(id_keys: list[str], values: list[str]) -> None:
    pyproject = tomlkit.parse((Path.cwd() / "pyproject.toml").read_text())

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

    (Path.cwd() / "pyproject.toml").write_text(tomlkit.dumps(pyproject))
