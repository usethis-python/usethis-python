from __future__ import annotations

import configparser
import re
from functools import singledispatch
from typing import TYPE_CHECKING

from configupdater import ConfigUpdater as INIDocument
from configupdater import Option, Section
from pydantic import TypeAdapter
from typing_extensions import assert_never

from usethis._integrations.file.ini.errors import (
    INIDecodeError,
    ININestingError,
    ININotFoundError,
    INIValueAlreadySetError,
    INIValueMissingError,
    InvalidINITypeError,
    UnexpectedINIIOError,
    UnexpectedINIOpenError,
)
from usethis._io import (
    KeyValueFileManager,
    UnexpectedFileIOError,
    UnexpectedFileOpenError,
    print_keys,
)

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence
    from pathlib import Path
    from typing import Any, ClassVar

    from typing_extensions import Self

    from usethis._io import (
        Key,
    )


class INIFileManager(KeyValueFileManager):
    _content_by_path: ClassVar[dict[Path, INIDocument | None]] = {}

    def __enter__(self) -> Self:
        try:
            return super().__enter__()
        except UnexpectedFileOpenError as err:
            raise UnexpectedINIOpenError(err) from None

    def read_file(self) -> None:
        try:
            super().read_file()
        except FileNotFoundError as err:
            raise ININotFoundError(err) from None
        except UnexpectedFileIOError as err:
            raise UnexpectedINIIOError(err) from None
        except configparser.ParsingError as err:
            msg = f"Failed to decode '{self.name}':\n{err}"
            raise INIDecodeError(msg) from None

    def _dump_content(self) -> str:
        if self._content is None:
            msg = "Content is None, cannot dump."
            raise ValueError(msg)

        return str(self._content)

    def _parse_content(self, content: str) -> INIDocument:
        updater = INIDocument()
        updater.read_string(content)
        return updater

    def get(self) -> INIDocument:
        return super().get()

    def commit(self, document: INIDocument) -> None:
        return super().commit(document)

    @property
    def _content(self) -> INIDocument | None:
        return super()._content

    @_content.setter
    def _content(self, value: INIDocument | None) -> None:
        self._content_by_path[self.path] = value

    def _validate_lock(self) -> None:
        try:
            super()._validate_lock()
        except UnexpectedFileIOError as err:
            raise UnexpectedINIIOError(err) from None

    def __contains__(self, keys: Sequence[Key]) -> bool:
        """Check if the INI file contains a value at the given key.

        An non-existent file will return False.
        """
        try:
            root = self.get()
        except FileNotFoundError:
            return False

        if len(keys) == 0:
            return True
        elif len(keys) == 1:
            (section_key,) = keys
            for _ in _itermatches(root.sections(), key=section_key):
                return True
        elif len(keys) == 2:
            (section_key, option_key) = keys
            for section_strkey in _itermatches(root.sections(), key=section_key):
                for _ in _itermatches(root[section_strkey].options(), key=option_key):
                    return True
        return False

    def __getitem__(self, item: Sequence[Key]) -> Any:
        keys = item

        root = self.get()

        if len(keys) == 0:
            return _as_dict(root)
        elif len(keys) == 1:
            (section_key,) = keys
            if not isinstance(section_key, str):
                msg = (
                    f"Only hard-coded strings are supported as keys when "
                    f"accessing values, but a {type(section_key)} was provided."
                )
                raise NotImplementedError(msg)
            return _as_dict(root[section_key])
        elif len(keys) == 2:
            (section_key, option_key) = keys
            if not isinstance(section_key, str) or not isinstance(option_key, str):
                msg = (
                    f"Only hard-coded strings are supported as keys when "
                    f"accessing values, but a {type(section_key)} was provided."
                )
                raise NotImplementedError(msg)
            return root[section_key][option_key].value
        else:
            msg = (
                f"INI files do not support nested config, whereas access to "
                f"'{self.name}' was attempted at '{print_keys(keys)}'."
            )
            raise KeyError(msg)

    def set_value(
        self, *, keys: Sequence[Key], value: Any, exists_ok: bool = False
    ) -> None:
        """Set a value in the INI file.

        An empty list of keys corresponds to the root of the document.
        """
        root = self.get()

        if len(keys) == 0:
            self._set_value_in_root(root=root, value=value, exists_ok=exists_ok)
        elif len(keys) == 1:
            (section_key,) = keys
            self._set_value_in_section(
                root=root, section_key=keys[0], value=value, exists_ok=exists_ok
            )
        elif len(keys) == 2:
            (section_key, option_key) = keys
            self._set_value_in_option(
                root=root,
                section_key=section_key,
                option_key=option_key,
                value=value,
                exists_ok=exists_ok,
            )
        else:
            msg = (
                f"INI files do not support nested config, whereas access to "
                f"'{self.name}' was attempted at '{print_keys(keys)}'."
            )
            raise ININestingError(msg)

        self.commit(root)

    @staticmethod
    def _set_value_in_root(
        root: INIDocument, value: dict[str, dict[str, str | list[str]]], exists_ok: bool
    ) -> None:
        root_dict = value

        if any(root) and not exists_ok:
            msg = "The INI file already has content at the root level."
            raise INIValueAlreadySetError(msg)

        # We need to remove section that are not in the new dict
        # We don't want to remove existing ones to keep their positions.
        for section_key in root.sections():
            if section_key not in root_dict:
                _remove_section(updater=root, section_key=section_key)

        TypeAdapter(dict).validate_python(root_dict)
        assert isinstance(root_dict, dict)

        for section_key, section_dict in root_dict.items():
            TypeAdapter(dict).validate_python(section_dict)
            assert isinstance(section_dict, dict)

            if section_key in root:
                for option_key in root[section_key]:
                    # We need to remove options that are not in the new dict
                    # We don't want to remove existing ones to keep their positions.
                    if option_key not in section_dict:
                        _remove_option(
                            updater=root, section_key=section_key, option_key=option_key
                        )
            else:
                root.add_section(section_key)

            for option_key, option in section_dict.items():
                INIFileManager._validated_set(
                    root=root,
                    section_key=section_key,
                    option_key=option_key,
                    value=option,
                )

    @staticmethod
    def _set_value_in_section(
        *,
        root: INIDocument,
        section_key: Key,
        value: dict[str, str | list[str]],
        exists_ok: bool,
    ) -> None:
        TypeAdapter(dict).validate_python(value)
        assert isinstance(value, dict)

        section_dict = value

        if section_key in root:
            if not exists_ok:
                msg = (
                    f"The INI file already has content at the section '{section_key}'."
                )
                raise INIValueAlreadySetError(msg)

            if not isinstance(section_key, str):
                msg = (
                    f"Only hard-coded strings are supported as section keys when "
                    f"setting values, but a {type(section_key)} was provided."
                )
                raise NotImplementedError(msg)

            for option_key in root[section_key]:
                # We need to remove options that are not in the new dict
                # We don't want to remove existing ones to keep their positions.
                if option_key not in section_dict:
                    _remove_option(
                        updater=root, section_key=section_key, option_key=option_key
                    )

        for option_key, option in section_dict.items():
            INIFileManager._validated_set(
                root=root,
                section_key=section_key,
                option_key=option_key,
                value=option,
            )

    @staticmethod
    def _set_value_in_option(
        *,
        root: INIDocument,
        section_key: Key,
        option_key: Key,
        value: str,
        exists_ok: bool,
    ) -> None:
        if not isinstance(section_key, str) or not isinstance(option_key, str):
            msg = (
                f"Only hard-coded strings are supported as keys when "
                f"setting values, but a {type(section_key)} was provided."
            )
            raise NotImplementedError(msg)

        if root.has_option(section=section_key, option=option_key) and not exists_ok:
            msg = (
                f"The INI file already has content at the section '{section_key}' "
                f"and option '{option_key}'."
            )
            raise INIValueAlreadySetError(msg)

        INIFileManager._validated_set(
            root=root, section_key=section_key, option_key=option_key, value=value
        )

    @staticmethod
    def _validated_set(
        *, root: INIDocument, section_key: Key, option_key: Key, value: str | list[str]
    ) -> None:
        if not isinstance(value, str | list):
            msg = (
                f"INI files only support strings (or lists of strings), but a "
                f"{type(value)} was provided."
            )
            raise InvalidINITypeError(msg)

        if not isinstance(section_key, str) or not isinstance(option_key, str):
            msg = (
                f"Only hard-coded strings are supported as keys when "
                f"setting values, but a {type(section_key)} was provided."
            )
            raise NotImplementedError(msg)

        if section_key not in root:
            _ensure_newline(root)
            root.add_section(section_key)

        root.set(section=section_key, option=option_key, value=value)

    @staticmethod
    def _validated_append(
        *, root: INIDocument, section_key: Key, option_key: Key, value: str
    ) -> None:
        if not isinstance(value, str):
            msg = (
                f"INI files only support strings (or lists of strings), but a "
                f"{type(value)} was provided."
            )
            raise InvalidINITypeError(msg)

        if not isinstance(section_key, str) or not isinstance(option_key, str):
            msg = (
                f"Only hard-coded strings are supported as keys when "
                f"setting values, but a {type(section_key)} was provided."
            )
            raise NotImplementedError(msg)

        if section_key not in root:
            root.add_section(section_key)

        if option_key not in root[section_key]:
            option = Option(key=option_key, value=value)
            root[section_key].add_option(option)
        else:
            root[section_key][option_key].append(value)

    def __delitem__(self, keys: Sequence[Key]) -> None:
        """Delete a value in the INI file.

        An empty list of keys corresponds to the root of the document.
        """
        # We will iterate through keys and find all matches in the document
        seqs: list[list[str]] = []

        if len(keys) == 0:
            seqs.append([])
        elif len(keys) == 1:
            (section_key,) = keys

            for seq in _itermatches(self.get().sections(), key=section_key):
                seqs.append([seq])
        elif len(keys) == 2:
            (section_key, option_key) = keys

            section_strkeys = []
            for section_strkey in _itermatches(self.get().sections(), key=section_key):
                section_strkeys.append(section_strkey)

            for section_strkey in section_strkeys:
                for option_strkey in _itermatches(
                    self.get()[section_strkey].options(), key=option_key
                ):
                    seqs.append([section_strkey, option_strkey])
        else:
            msg = (
                f"INI files do not support nested config, whereas access to "
                f"'{self.name}' was attempted at '{print_keys(keys)}'."
            )
            raise ININestingError(msg)

        if not seqs:
            msg = f"INI file '{self.name}' does not contain the keys '{print_keys(keys)}'."
            raise INIValueMissingError(msg)

        for seq in seqs:
            self._delete_strkeys(seq)

    def _delete_strkeys(self, strkeys: Sequence[str]) -> None:
        """Delete a specific value in the INI file.

        An empty list of strkeys corresponds to the root of the document.

        Assumes that the keys exist in the file.
        """
        root = self.get()

        if len(strkeys) == 0:
            removed = False
            for section_key in root.sections():
                removed |= _remove_section(updater=root, section_key=section_key)
        elif len(strkeys) == 1:
            (section_key,) = strkeys
            removed = _remove_section(updater=root, section_key=section_key)
        elif len(strkeys) == 2:
            section_key, option_key = strkeys
            removed = _remove_option(
                updater=root, section_key=section_key, option_key=option_key
            )

            # Cleanup section if empty
            if not root[section_key].options():
                _remove_section(updater=root, section_key=section_key)
        else:
            msg = (
                f"INI files do not support nested config, whereas access to "
                f"'{self.name}' was attempted at '{print_keys(strkeys)}'."
            )
            raise ININestingError(msg)

        if not removed:
            msg = f"INI file '{self.name}' does not contain the keys '{print_keys(strkeys)}'."
            raise INIValueMissingError(msg)

        self.commit(root)

    def extend_list(self, *, keys: Sequence[Key], values: list[str]) -> None:
        """Extend a list in the INI file.

        An empty list of keys corresponds to the root of the document.
        """
        root = self.get()

        if len(keys) == 0:
            msg = (
                f"INI files do not support lists at the root level, whereas access to "
                f"'{self.name}' was attempted at '{print_keys(keys)}'."
            )
            raise InvalidINITypeError(msg)
        elif len(keys) == 1:
            msg = (
                f"INI files do not support lists at the section level, whereas access "
                f"to '{self.name}' was attempted at '{print_keys(keys)}'."
            )
            raise InvalidINITypeError(msg)
        elif len(keys) == 2:
            section_key, option_key = keys
            self._extend_list_in_option(
                root=root, section_key=section_key, option_key=option_key, values=values
            )
        else:
            msg = (
                f"INI files do not support nested config, whereas access to "
                f"'{self.name}' was attempted at '{print_keys(keys)}'."
            )
            raise ININestingError(msg)

        self.commit(root)

    @staticmethod
    def _extend_list_in_option(
        *, root: INIDocument, section_key: Key, option_key: Key, values: list[str]
    ) -> None:
        for value in values:
            INIFileManager._validated_append(
                root=root, section_key=section_key, option_key=option_key, value=value
            )

    @staticmethod
    def _remove_from_list_in_option(
        *, root: INIDocument, section_key: Key, option_key: Key, values: list[str]
    ) -> None:
        if section_key not in root:
            return

        if option_key not in root[section_key]:
            return

        if not isinstance(section_key, str) or not isinstance(option_key, str):
            msg = (
                f"Only hard-coded strings are supported as keys when "
                f"modifying values, but a {type(section_key)} was provided."
            )
            raise NotImplementedError(msg)

        original_values = root[section_key][option_key].as_list()
        # If already not present, silently pass
        new_values = [value for value in original_values if value not in values]

        if len(new_values) == 0:
            # Remove the option if empty
            _remove_option(updater=root, section_key=section_key, option_key=option_key)

            # Remove the section if empty
            if not root[section_key].options():
                _remove_section(updater=root, section_key=section_key)

        elif len(new_values) == 1:
            # If only one value left, set it directly
            root[section_key][option_key] = new_values[0]
        elif len(new_values) > 1:
            root[section_key][option_key].set_values(new_values)

    def remove_from_list(self, *, keys: Sequence[Key], values: list[str]) -> None:
        """Remove values from a list in the INI file.

        An empty list of keys corresponds to the root of the document.
        """
        root = self.get()

        if len(keys) == 0:
            msg = (
                f"INI files do not support lists at the root level, whereas access to "
                f"'{self.name}' was attempted at '{print_keys(keys)}'."
            )
            raise InvalidINITypeError(msg)
        elif len(keys) == 1:
            msg = (
                f"INI files do not support lists at the section level, whereas access "
                f"to '{self.name}' was attempted at '{print_keys(keys)}'."
            )
            raise InvalidINITypeError(msg)
        elif len(keys) == 2:
            section_key, option_key = keys
            self._remove_from_list_in_option(
                root=root, section_key=section_key, option_key=option_key, values=values
            )
        else:
            msg = (
                f"INI files do not support nested config, whereas access to "
                f"'{self.name}' was attempted at '{print_keys(keys)}'."
            )
            raise ININestingError(msg)

        self.commit(root)


@singledispatch
def _as_dict(
    value: INIDocument | Section,
) -> dict[str, dict[str, Any]] | dict[str, Any]:
    raise NotImplementedError


@_as_dict.register(INIDocument)
def _(value: INIDocument) -> dict[str, dict[str, Any]]:
    return {k: _as_dict(v) for k, v in value.items()}


@_as_dict.register(Section)
def _(value: Section) -> dict[str, Any]:
    return {option.key: option.value for option in value.iter_options()}


def _remove_option(updater: INIDocument, section_key: str, option_key: str) -> bool:
    try:
        return updater.remove_option(section=section_key, option=option_key)
    except configparser.NoSectionError as err:
        raise INIValueMissingError(err) from None


def _remove_section(updater: INIDocument, section_key: str) -> bool:
    return updater.remove_section(name=section_key)


def _itermatches(values: Iterable[str], /, *, key: Key):
    """Iterate through an iterable and find all matches for a key."""
    for value in values:
        if isinstance(key, str):
            if key == value:
                yield value
        elif isinstance(key, re.Pattern):
            if key.fullmatch(value):
                yield value
        else:
            assert_never(key)


def _ensure_newline(root: INIDocument) -> None:
    """Add a newline to the INI file."""
    sections = list(root.iter_sections())
    if not sections:
        # No newline necessary
        return
    final_section = sections[-1]
    final_section.add_after.space(newlines=1)
