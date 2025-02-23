from pydantic import TypeAdapter
from tomlkit import TOMLDocument

from usethis._integrations.toml.errors import TOMLValueMissingError


def remove_toml_value(
    *,
    toml_document: TOMLDocument,
    id_keys: list[str],
) -> TOMLDocument:
    if not id_keys:
        msg = "At least one ID key must be provided."
        raise ValueError(msg)

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
