from typing import Any

import mergedeep
from pydantic import TypeAdapter
from tomlkit.toml_document import TOMLDocument

from usethis._integrations.pyproject_toml.errors import (
    PyprojectTOMLValueAlreadySetError,
    PyprojectTOMLValueMissingError,
)
from usethis._integrations.pyproject_toml.io_ import (
    read_pyproject_toml,
    write_pyproject_toml,
)
from usethis._integrations.toml.core import remove_toml_value, set_toml_value
from usethis._integrations.toml.errors import (
    TOMLValueAlreadySetError,
    TOMLValueMissingError,
)


def get_config_value(id_keys: list[str]) -> Any:
    if not id_keys:
        msg = "At least one ID key must be provided."
        raise ValueError(msg)

    pyproject = read_pyproject_toml()

    p = pyproject
    for key in id_keys:
        TypeAdapter(dict).validate_python(p)
        assert isinstance(p, dict)
        p = p[key]

    return p


def set_config_value(
    id_keys: list[str], value: Any, *, exists_ok: bool = False
) -> None:
    """Set a value in the pyproject.toml configuration file."""
    pyproject = read_pyproject_toml()

    try:
        pyproject = set_toml_value(
            toml_document=pyproject, id_keys=id_keys, value=value, exists_ok=exists_ok
        )
    except TOMLValueAlreadySetError as err:
        raise PyprojectTOMLValueAlreadySetError(err)

    write_pyproject_toml(pyproject)


def remove_config_value(id_keys: list[str], *, missing_ok: bool = False) -> None:
    """Remove a value from the pyproject.toml configuration file."""
    pyproject = read_pyproject_toml()

    try:
        pyproject = remove_toml_value(toml_document=pyproject, id_keys=id_keys)
    except TOMLValueMissingError as err:
        if not missing_ok:
            raise PyprojectTOMLValueMissingError(err)
        # Otherwise, no changes are needed so skip the write step.
        return
    write_pyproject_toml(pyproject)


def append_config_list(
    id_keys: list[str],
    values: list[Any],
) -> None:
    """Append values to a list in the pyproject.toml configuration file."""
    if not id_keys:
        msg = "At least one ID key must be provided."
        raise ValueError(msg)

    pyproject = read_pyproject_toml()

    try:
        p = pyproject
        for key in id_keys[:-1]:
            TypeAdapter(dict).validate_python(p)
            assert isinstance(p, dict)
            p = p[key]
        p_parent = p
        TypeAdapter(dict).validate_python(p_parent)
        assert isinstance(p_parent, dict)
        p = p_parent[id_keys[-1]]
    except KeyError:
        contents = values
        for key in reversed(id_keys):
            contents = {key: contents}
        assert isinstance(contents, dict)
        pyproject = mergedeep.merge(pyproject, contents)
        assert isinstance(pyproject, TOMLDocument)
    else:
        TypeAdapter(dict).validate_python(p_parent)
        TypeAdapter(list).validate_python(p)
        assert isinstance(p_parent, dict)
        assert isinstance(p, list)
        p_parent[id_keys[-1]] = p + values

    write_pyproject_toml(pyproject)


def remove_from_config_list(id_keys: list[str], values: list[str]) -> None:
    if not id_keys:
        msg = "At least one ID key must be provided."
        raise ValueError(msg)

    pyproject = read_pyproject_toml()

    try:
        p = pyproject
        for key in id_keys[:-1]:
            TypeAdapter(dict).validate_python(p)
            assert isinstance(p, dict)
            p = p[key]

        p_parent = p
        TypeAdapter(dict).validate_python(p_parent)
        assert isinstance(p_parent, dict)
        p = p_parent[id_keys[-1]]
    except KeyError:
        # The configuration is not present.
        return

    TypeAdapter(dict).validate_python(p_parent)
    TypeAdapter(list).validate_python(p)
    assert isinstance(p_parent, dict)
    assert isinstance(p, list)

    new_values = [value for value in p if value not in values]
    p_parent[id_keys[-1]] = new_values

    write_pyproject_toml(pyproject)


def do_id_keys_exist(id_keys: list[str]) -> bool:
    pyproject = read_pyproject_toml()

    try:
        for key in id_keys:
            TypeAdapter(dict).validate_python(pyproject)
            assert isinstance(pyproject, dict)
            pyproject = pyproject[key]
    except KeyError:
        return False

    return True
