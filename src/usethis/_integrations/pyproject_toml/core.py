from typing import Any

from usethis._integrations.pyproject_toml.errors import (
    PyprojectTOMLValueAlreadySetError,
    PyprojectTOMLValueMissingError,
)
from usethis._integrations.pyproject_toml.io_ import (
    read_pyproject_toml,
    write_pyproject_toml,
)
from usethis._integrations.toml.core import (
    do_toml_id_keys_exist,
    extend_toml_list,
    get_toml_value,
    remove_from_toml_list,
    remove_toml_value,
    set_toml_value,
)
from usethis._integrations.toml.errors import (
    TOMLValueAlreadySetError,
    TOMLValueMissingError,
)


def get_pyproject_value(id_keys: list[str]) -> Any:
    if not id_keys:
        msg = "At least one ID key must be provided."
        raise ValueError(msg)

    pyproject = read_pyproject_toml()

    return get_toml_value(toml_document=pyproject, id_keys=id_keys)


def set_pyproject_value(
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


def remove_pyproject_value(
    id_keys: list[str],
    *,
    missing_ok: bool = False,
) -> None:
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


def extend_pyproject_list(
    id_keys: list[str],
    values: list[Any],
) -> None:
    """Append values to a list in the pyproject.toml configuration file."""
    pyproject = read_pyproject_toml()

    pyproject = extend_toml_list(
        toml_document=pyproject,
        id_keys=id_keys,
        values=values,
    )

    write_pyproject_toml(pyproject)


def remove_from_pyproject_list(id_keys: list[str], values: list[str]) -> None:
    pyproject = read_pyproject_toml()

    pyproject = remove_from_toml_list(
        toml_document=pyproject,
        id_keys=id_keys,
        values=values,
    )

    write_pyproject_toml(pyproject)


def do_pyproject_id_keys_exist(id_keys: list[str]) -> bool:
    pyproject = read_pyproject_toml()

    return do_toml_id_keys_exist(
        toml_document=pyproject,
        id_keys=id_keys,
    )
