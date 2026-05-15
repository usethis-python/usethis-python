"""YAML file I/O manager."""

from __future__ import annotations

import re
from abc import ABCMeta
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar

import yamltrip
from pydantic import TypeAdapter, ValidationError
from typing_extensions import assert_never, override

from usethis._file.manager import (
    KeyValueFileManager,
    UnexpectedFileIOError,
    UnexpectedFileOpenError,
)
from usethis._file.print_ import print_keys
from usethis._file.yaml.errors import (
    UnexpectedYAMLIOError,
    UnexpectedYAMLOpenError,
    UnexpectedYAMLValueError,
    YAMLDecodeError,
    YAMLNotFoundError,
    YAMLValueAlreadySetError,
    YAMLValueMissingError,
)

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    from typing_extensions import Self

    from usethis._file.types_ import Key


@dataclass
class YAMLDocument:
    """A dataclass to represent a YAML document in memory.

    Attributes:
        doc: The yamltrip Document holding the parsed YAML source.
    """

    doc: yamltrip.Document


class YAMLFileManager(KeyValueFileManager["YAMLDocument"], metaclass=ABCMeta):
    """An abstract class for managing YAML files."""

    _content_by_path: ClassVar[dict[Path, YAMLDocument | None]] = {}

    @override
    def __enter__(self) -> Self:
        try:
            return super().__enter__()
        except UnexpectedFileOpenError as err:
            raise UnexpectedYAMLOpenError(err) from None

    @override
    def read_file(self) -> YAMLDocument:
        try:
            return super().read_file()
        except FileNotFoundError as err:
            raise YAMLNotFoundError(err) from None
        except UnexpectedFileIOError as err:
            raise UnexpectedYAMLIOError(err) from None
        except yamltrip.ParseError as err:
            msg = f"Failed to decode '{self.name}':\n{err}"
            raise YAMLDecodeError(msg) from None

    @override
    def _dump_content(self) -> str:
        if self._content is None:
            msg = "Content is None, cannot dump."
            raise ValueError(msg)

        return self._content.doc.dumps()

    @override
    def get(self) -> YAMLDocument:
        return super().get()

    @override
    def commit(self, document: YAMLDocument) -> None:
        return super().commit(document)

    @override
    def _parse_content(self, content: str) -> YAMLDocument:
        return YAMLDocument(doc=yamltrip.loads(content))

    @property
    @override
    def _content(self) -> YAMLDocument | None:
        return self._content_by_path.get(self.path)

    @_content.setter
    def _content(self, value: YAMLDocument | None) -> None:
        self._content_by_path[self.path] = value

    @override
    def _validate_lock(self) -> None:
        try:
            super()._validate_lock()
        except UnexpectedFileIOError as err:
            raise UnexpectedYAMLIOError(err) from None

    @override
    def __contains__(self, keys: Sequence[Key]) -> bool:
        """Check if the YAML file contains a value.

        A non-existent file will return False.
        An empty keys sequence checks whether the document root exists.
        """
        keys = _validate_keys(keys)

        try:
            doc = self.get().doc
        except FileNotFoundError:
            return False

        if not keys:
            return True

        return tuple(keys) in doc

    @override
    def __getitem__(self, item: Sequence[Key]) -> object:
        keys = _validate_keys(item)

        doc = self.get().doc
        try:
            result = doc[tuple(keys)]
        except yamltrip.QueryError as err:
            if not keys:
                return {}
            msg = f"Configuration value '{print_keys(keys)}' is missing."
            raise YAMLValueMissingError(msg) from err
        return result

    @override
    def set_value(
        self, *, keys: Sequence[Key], value: Any, exists_ok: bool = False
    ) -> None:
        """Set a value in the YAML file.

        An empty list of keys corresponds to the root of the document.
        """
        keys = _validate_keys(keys)
        yaml_doc = self.get()
        doc = yaml_doc.doc

        if not keys:
            # Root level: value must be a mapping.
            try:
                TypeAdapter(dict).validate_python(value)
            except ValidationError:
                msg = "Root level configuration must be a mapping."
                raise UnexpectedYAMLValueError(msg) from None
            assert isinstance(value, dict)

            for k, v in value.items():
                if not exists_ok and (k,) in doc:
                    msg = f"Configuration value '{print_keys([k])}' is already set."
                    raise YAMLValueAlreadySetError(msg)
                doc = _upsert_safe(doc, (k,), v, exists_ok=exists_ok)
        else:
            # Validate root is a mapping before attempting key insertion.
            try:
                root = doc[()]
            except yamltrip.QueryError:
                root = None
            if root is not None and not isinstance(root, dict):
                msg = "Root level configuration must be a mapping."
                raise UnexpectedYAMLValueError(msg)
            if not exists_ok and tuple(keys) in doc:
                msg = f"Configuration value '{print_keys(keys)}' is already set."
                raise YAMLValueAlreadySetError(msg)
            doc = _upsert_safe(doc, tuple(keys), value, exists_ok=exists_ok)

        self.commit(YAMLDocument(doc=doc))

    @override
    def __delitem__(self, keys: Sequence[Key]) -> None:
        """Delete a value in the YAML file.

        An empty list of keys corresponds to the root of the document.

        Trying to delete a key from a document that doesn't exist will pass silently.
        """
        try:
            yaml_doc = self.get()
        except FileNotFoundError:
            return
        keys = _validate_keys(keys)
        doc = yaml_doc.doc

        if not keys:
            # Delete root: remove all top-level keys.
            try:
                root = doc[()]
            except yamltrip.QueryError:
                msg = f"Configuration value '{print_keys(keys)}' is missing."
                raise YAMLValueMissingError(msg) from None
            if not isinstance(root, dict):
                msg = f"Configuration value '{print_keys(keys)}' is missing."
                raise YAMLValueMissingError(msg)
            for k in list(root.keys()):
                doc = doc.remove(k)
        else:
            try:
                doc = doc.prune_remove(*keys)
            except yamltrip.QueryError:
                msg = f"Configuration value '{print_keys(keys)}' is missing."
                raise YAMLValueMissingError(msg) from None
            except yamltrip.PatchError:
                msg = f"Configuration value '{print_keys(keys)}' is missing."
                raise YAMLValueMissingError(msg) from None

        self.commit(YAMLDocument(doc=doc))

    @override
    def extend_list(self, *, keys: Sequence[Key], values: Sequence[Any]) -> None:
        """Extend a list in the configuration file."""
        if not keys:
            msg = "At least one ID key must be provided."
            raise ValueError(msg)
        keys = _validate_keys(keys)
        yaml_doc = self.get()
        doc = yaml_doc.doc

        # Validate root is a mapping.
        try:
            root = doc[()]
        except yamltrip.QueryError:
            root = None
        if root is not None and not isinstance(root, dict):
            msg = "Root level configuration must be a mapping."
            raise UnexpectedYAMLValueError(msg)

        if tuple(keys) in doc:
            try:
                doc = doc.extend_list(*keys, values=list(values))
            except yamltrip.PatchError:
                # Flow sequence or other issue — rebuild with merged list.
                existing = doc[tuple(keys)]
                if isinstance(existing, list):
                    new_list = existing + list(values)
                else:
                    new_list = list(values)
                doc = _upsert_complex(doc, tuple(keys), new_list, exists_ok=True)
        else:
            doc = _upsert_safe(doc, tuple(keys), list(values), exists_ok=False)

        self.commit(YAMLDocument(doc=doc))

    @override
    def remove_from_list(self, *, keys: Sequence[Key], values: Sequence[Any]) -> None:
        """Remove values from a list in the configuration file."""
        if not keys:
            msg = "At least one ID key must be provided."
            raise ValueError(msg)
        keys = _validate_keys(keys)
        yaml_doc = self.get()
        doc = yaml_doc.doc

        # Validate root is a mapping.
        try:
            root = doc[()]
        except yamltrip.QueryError:
            root = None
        if root is not None and not isinstance(root, dict):
            msg = "Root level configuration must be a mapping."
            raise UnexpectedYAMLValueError(msg)

        if tuple(keys) not in doc:
            return

        try:
            doc = doc.remove_from_list(*keys, values=list(values))
        except yamltrip.PatchError:
            # Value at the path is not a list; treat as no-op.
            return
        self.commit(YAMLDocument(doc=doc))


def _validate_keys(keys: Sequence[Key]) -> list[str]:
    """Validate the keys.

    Args:
        keys: The keys to validate.

    Raises:
        ValueError: If the keys are not valid.
    """
    so_far_keys: list[str] = []
    for key in keys:
        if isinstance(key, str):
            so_far_keys.append(key)
        elif isinstance(key, re.Pattern):
            msg = (
                f"Regex-based keys are not currently supported in YAML files: "
                f"{print_keys([*so_far_keys, key])}"
            )
            raise NotImplementedError(msg)
        else:
            assert_never(key)

    return so_far_keys


def _upsert_safe(
    doc: yamltrip.Document,
    keys: tuple[str, ...],
    value: Any,
    *,
    exists_ok: bool = False,
) -> yamltrip.Document:
    """Upsert a value into a yamltrip Document, handling empty documents."""
    # For complex values (list/dict), use the document rebuild approach
    # since yamltrip can only upsert/replace scalar values.
    if isinstance(value, (list, dict)):
        return _upsert_complex(doc, keys, value, exists_ok=exists_ok)

    try:
        return doc.upsert(*keys, value=value)
    except yamltrip.PatchError as err:
        if not doc.source.strip():
            # Empty document: bootstrap with a seed mapping and upsert.
            doc = yamltrip.loads("{}\n")
            return doc.upsert(*keys, value=value)
        err_msg = str(err)
        if (
            "non-mapping route" in err_msg
            or "expected mapping containing key" in err_msg
        ):
            if exists_ok:
                # Remove the conflicting prefix and retry.
                for i in range(len(keys) - 1, 0, -1):
                    if tuple(keys[:i]) in doc:
                        doc = doc.prune_remove(*keys[:i])
                        return _upsert_safe(doc, keys, value, exists_ok=exists_ok)
            # Trying to add a key under a non-mapping node.
            # Find the longest existing prefix to report.
            for i in range(len(keys) - 1, 0, -1):
                if tuple(keys[:i]) in doc:
                    msg = f"Configuration value '{print_keys(list(keys[:i]))}' is already set."
                    raise YAMLValueAlreadySetError(msg) from err
        raise


def _upsert_complex(
    doc: yamltrip.Document,
    keys: tuple[str, ...],
    value: Any,
    *,
    exists_ok: bool = False,
) -> yamltrip.Document:
    """Upsert a complex value (list/dict) by rebuilding the document text."""
    # Remove existing key if present
    if tuple(keys) in doc:
        if not exists_ok:
            msg = f"Configuration value '{print_keys(list(keys))}' is already set."
            raise YAMLValueAlreadySetError(msg)
        doc = doc.prune_remove(*keys)

    # Serialize the new key-value pair to YAML text
    key_path = keys[-1] if keys else ""
    indent_level = len(keys) - 1
    value_yaml = _serialize_yaml_value(value, indent=indent_level + 1)
    prefix = "  " * indent_level
    key_yaml = f"{prefix}{key_path}:\n{value_yaml}\n"

    # For nested keys, we need to navigate into the parent.
    # For simplicity, handle only the common case: single key at root level.
    if len(keys) == 1:
        base_text = doc.source if doc.source.strip() else ""
        if base_text and not base_text.endswith("\n"):
            base_text += "\n"
        new_text = base_text + key_yaml
        try:
            return yamltrip.loads(new_text)
        except yamltrip.ParseError:
            # Text concatenation failed (e.g., flow mapping root). Fall through
            # to full rebuild.
            pass

    # For deeper keys, fall back to rebuilding the full document.
    try:
        root = doc[()]
    except yamltrip.QueryError:
        root = {}
    if not isinstance(root, dict):
        root = {}
    _deep_set(root, list(keys), value)
    new_text = _serialize_yaml_mapping(root)
    return yamltrip.loads(new_text)


def _deep_set(d: dict[str, Any], keys: list[str], value: Any) -> None:
    """Set a value at a nested key path in a dict."""
    for key in keys[:-1]:
        if key not in d or not isinstance(d[key], dict):
            d[key] = {}
        d = d[key]
    d[keys[-1]] = value


def _serialize_yaml_mapping(mapping: dict[str, Any], indent: int = 0) -> str:
    """Serialize a dict to YAML block-style text."""
    lines: list[str] = []
    prefix = "  " * indent
    for k, v in mapping.items():
        if isinstance(v, (dict, list)):
            lines.append(f"{prefix}{k}:")
            lines.append(_serialize_yaml_value(v, indent=indent + 1))
        else:
            lines.append(f"{prefix}{k}: {_serialize_yaml_scalar(v)}")
    return "\n".join(lines) + "\n"


def _serialize_yaml_value(value: Any, indent: int = 0) -> str:
    """Serialize a Python value to YAML text at the given indentation level."""
    prefix = "  " * indent
    if isinstance(value, dict):
        return _serialize_yaml_dict_value(value, prefix, indent)
    if isinstance(value, list):
        return _serialize_yaml_list_value(value, prefix, indent)
    return f"{prefix}{_serialize_yaml_scalar(value)}"


def _serialize_yaml_dict_value(value: dict[str, Any], prefix: str, indent: int) -> str:
    if not value:
        return f"{prefix}{{}}"
    lines: list[str] = []
    for k, v in value.items():
        if isinstance(v, (dict, list)):
            lines.append(f"{prefix}{k}:")
            lines.append(_serialize_yaml_value(v, indent=indent + 1))
        else:
            lines.append(f"{prefix}{k}: {_serialize_yaml_scalar(v)}")
    return "\n".join(lines)


def _serialize_yaml_list_value(value: list[Any], prefix: str, indent: int) -> str:
    if not value:
        return f"{prefix}[]"
    lines: list[str] = []
    for item in value:
        if isinstance(item, dict):
            first = True
            for k, v in item.items():
                item_prefix = f"{prefix}- " if first else f"{prefix}  "
                if isinstance(v, (dict, list)):
                    lines.append(f"{item_prefix}{k}:")
                    lines.append(_serialize_yaml_value(v, indent=indent + 2))
                else:
                    lines.append(f"{item_prefix}{k}: {_serialize_yaml_scalar(v)}")
                first = False
        else:
            lines.append(f"{prefix}- {_serialize_yaml_scalar(item)}")
    return "\n".join(lines)


def _serialize_yaml_scalar(value: Any) -> str:
    """Serialize a scalar Python value to its YAML representation."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return _serialize_yaml_string(value)
    return str(value)


def _serialize_yaml_string(value: str) -> str:
    _YAML_KEYWORDS = {"true", "false", "null", "yes", "no", "on", "off"}
    needs_quoting = (
        value == ""
        or value in _YAML_KEYWORDS
        or value.startswith(("{", "[", "'", '"', "*", "&", "!", "|", ">"))
        or "#" in value
        or ": " in value
        or value.endswith(":")
    )
    if needs_quoting:
        escaped = value.replace("'", "''")
        return f"'{escaped}'"
    return value
