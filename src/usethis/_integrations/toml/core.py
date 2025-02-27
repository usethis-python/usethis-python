import copy
from typing import Any

import mergedeep
from pydantic import TypeAdapter
from tomlkit import TOMLDocument

from usethis._integrations.toml.errors import (
    TOMLValueAlreadySetError,
    TOMLValueMissingError,
)


def set_toml_value(
    *,
    toml_document: TOMLDocument,
    id_keys: list[str],
    value: Any,
    exists_ok: bool = False,
) -> TOMLDocument:
    if not id_keys:
        msg = "At least one ID key must be provided."
        raise ValueError(msg)

    toml_document = copy.copy(toml_document)

    try:
        # Index our way into each ID key.
        # Eventually, we should land at a final dict, which is the one we are setting.
        d, parent = toml_document, {}
        for key in id_keys:
            TypeAdapter(dict).validate_python(d)
            assert isinstance(d, dict)
            d, parent = d[key], d
    except KeyError:
        # The old configuration should be kept for all ID keys except the
        # final/deepest one which shouldn't exist anyway since we checked as much,
        # above. For example, if there is [tool.ruff] then we shouldn't overwrite it
        # with [tool.deptry]; they should coexist. So under the "tool" key, we need
        # to merge the two dicts.
        contents = value
        for key in reversed(id_keys):
            contents = {key: contents}
        toml_document = mergedeep.merge(toml_document, contents)  # type: ignore[reportAssignmentType]
        assert isinstance(toml_document, TOMLDocument)
    else:
        if not exists_ok:
            # The configuration is already present, which is not allowed.
            msg = f"Configuration value '{'.'.join(id_keys)}' is already set."
            raise TOMLValueAlreadySetError(msg)
        else:
            # The configuration is already present, but we're allowed to overwrite it.
            TypeAdapter(dict).validate_python(parent)
            assert isinstance(parent, dict)
            parent[id_keys[-1]] = value

    return toml_document


def remove_toml_value(
    *,
    toml_document: TOMLDocument,
    id_keys: list[str],
) -> TOMLDocument:
    if not id_keys:
        msg = "At least one ID key must be provided."
        raise ValueError(msg)

    toml_document = copy.copy(toml_document)

    # Exit early if the configuration is not present.
    try:
        d = toml_document
        for key in id_keys:
            TypeAdapter(dict).validate_python(d)
            assert isinstance(d, dict)
            d = d[key]
    except KeyError:
        msg = f"Configuration value '{'.'.join(id_keys)}' is missing."
        raise TOMLValueMissingError(msg)

    # Remove the configuration.
    d = toml_document
    for key in id_keys[:-1]:
        TypeAdapter(dict).validate_python(d)
        assert isinstance(d, dict)
        d = d[key]
    assert isinstance(d, dict)
    del d[id_keys[-1]]

    # Cleanup: any empty sections should be removed.
    for idx in range(len(id_keys) - 1):
        d, parent = toml_document, {}
        TypeAdapter(dict).validate_python(d)
        for key in id_keys[: idx + 1]:
            d, parent = d[key], d
            TypeAdapter(dict).validate_python(d)
            TypeAdapter(dict).validate_python(parent)
            assert isinstance(d, dict)
            assert isinstance(parent, dict)
        assert isinstance(d, dict)
        if not d:
            del parent[id_keys[idx]]

    return toml_document
