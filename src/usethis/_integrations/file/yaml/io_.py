from __future__ import annotations

import contextlib
import copy
import re
from abc import abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass
from io import StringIO
from typing import TYPE_CHECKING, Any, ClassVar

import ruamel.yaml
from pydantic import TypeAdapter
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.error import YAMLError
from ruamel.yaml.util import load_yaml_guess_indent
from typing_extensions import assert_never

from usethis._console import info_print
from usethis._integrations.file.yaml.errors import (
    UnexpectedYAMLIOError,
    UnexpectedYAMLOpenError,
    YAMLDecodeError,
    YAMLNotFoundError,
    YAMLValueMissingError,
)
from usethis._integrations.file.yaml.update import update_ruamel_yaml_map
from usethis._io import (
    KeyValueFileManager,
    UnexpectedFileIOError,
    UnexpectedFileOpenError,
    print_keys,
)

if TYPE_CHECKING:
    from collections.abc import Generator, Sequence
    from io import TextIOWrapper
    from pathlib import Path
    from types import NoneType
    from typing import TypeAlias

    from ruamel.yaml.comments import (
        CommentedOrderedMap,
        CommentedSeq,
        CommentedSet,
        TaggedScalar,
    )
    from ruamel.yaml.scalarbool import ScalarBoolean
    from ruamel.yaml.scalarfloat import ScalarFloat
    from ruamel.yaml.scalarint import BinaryInt, HexCapsInt, HexInt, OctalInt, ScalarInt
    from ruamel.yaml.scalarstring import FoldedScalarString, LiteralScalarString
    from ruamel.yaml.timestamp import TimeStamp
    from typing_extensions import Self

    from usethis._io import Key

    YAMLLiteral: TypeAlias = (
        NoneType
        | bool
        | float
        | int
        | str
        | BinaryInt
        | FoldedScalarString
        | HexInt
        | HexCapsInt
        | LiteralScalarString
        | OctalInt
        | ScalarBoolean
        | ScalarFloat
        | ScalarInt
        | TaggedScalar
        | TimeStamp
        | CommentedSeq
        | CommentedSet
        | CommentedOrderedMap
        | CommentedMap
    )


class YAMLFileManager(KeyValueFileManager):
    _content_by_path: ClassVar[dict[Path, YAMLDocument | None]] = {}

    @property
    @abstractmethod
    def relative_path(self) -> Path:
        """Return the relative path to the file."""
        raise NotImplementedError

    def __enter__(self) -> Self:
        try:
            return super().__enter__()
        except UnexpectedFileOpenError as err:
            raise UnexpectedYAMLOpenError(err) from None

    def read_file(self) -> None:
        try:
            super().read_file()
        except FileNotFoundError as err:
            raise YAMLNotFoundError(err) from None
        except UnexpectedFileIOError as err:
            raise UnexpectedYAMLIOError(err) from None
        except YAMLError as err:
            msg = f"Failed to decode '{self.name}':\n{err}"
            raise YAMLDecodeError(msg) from None

    def _dump_content(self) -> str:
        """Return the content of the document as a string."""
        if self._content is None:
            msg = "Content is None, cannot dump."
            raise ValueError(msg)

        output = StringIO()
        self._content.roundtripper.dump(self._content.content, output)
        return output.getvalue()

    def _parse_content(self, content: str) -> YAMLDocument:
        """Parse the content of the document."""
        return _get_yaml_document(StringIO(content), guess_indent=True)

    @property
    def _content(self) -> YAMLDocument | None:
        return self._content_by_path.get(self.path)

    @_content.setter
    def _content(self, value: YAMLDocument | None) -> None:
        self._content_by_path[self.path] = value

    def __contains__(self, keys: Sequence[Key]) -> bool:
        """Check if a key exists in the configuration file."""
        keys = _validate_keys(keys)

        # Check if the keys exist in the content.
        try:
            current = self.get().content
        except FileNotFoundError:
            return False
        try:
            for key in keys:
                if isinstance(current, CommentedMap):
                    current = current[key]
                else:
                    return False
        except KeyError:
            return False
        return True

    def __getitem__(self, keys: Sequence[Key]) -> Any:
        """Get a value from the configuration file."""
        keys = _validate_keys(keys)

        d = self.get().content
        for key in keys:
            TypeAdapter(dict).validate_python(d)
            assert isinstance(d, dict)
            d = d[key]

        return d

    def get(self) -> YAMLDocument:
        return super().get()

    def __delitem__(self, keys: Sequence[Key]) -> None:
        """Remove a value from the configuration file."""
        try:
            content = copy.copy(self.get().content)
        except FileNotFoundError:
            return
        TypeAdapter(dict).validate_python(content)
        assert isinstance(content, dict)
        keys = _validate_keys(keys)

        # Exit early if the configuration is not present.
        try:
            d = content
            for key in keys:
                TypeAdapter(dict).validate_python(d)
                assert isinstance(d, dict)
                d = d[key]
        except KeyError:
            # N.B. by convention a del call should raise an error if the key is not found.
            msg = f"Configuration value '{print_keys(keys)}' is missing."
            raise YAMLValueMissingError(msg) from None

        # Remove the configuration.
        d = content
        for key in keys[:-1]:
            TypeAdapter(dict).validate_python(d)
            assert isinstance(d, dict)
            d = d[key]
        assert isinstance(d, dict)
        if not keys:
            # i.e. the case where we're deleting the root of the document.
            for key in list(d.keys()):
                del d[key]
        else:
            with contextlib.suppress(KeyError):
                d.__delitem__(keys[-1])

            # Cleanup: any empty sections should be removed.
            for idx in reversed(range(1, len(keys))):
                # Navigate to the parent of the section we want to check
                parent = content
                for key in keys[: idx - 1]:
                    TypeAdapter(dict).validate_python(parent)
                    assert isinstance(parent, dict)
                    parent = parent[key]

                # If the section is empty, remove it
                TypeAdapter(dict).validate_python(parent)
                assert isinstance(parent, dict)
                if not parent[keys[idx - 1]]:
                    del parent[keys[idx - 1]]

        assert self._content is not None  # We have called .get() already.
        update_ruamel_yaml_map(
            cmap=self._content.content,
            new_contents=content,
            preserve_comments=True,
        )
        self.commit(self._content)


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
            # Currently no need for this, perhaps we may add it in the future.
            msg = (
                f"Regex-based keys are not currently supported in YAML files: "
                f"{print_keys([*so_far_keys, key])}"
            )
            raise NotImplementedError(msg)
        else:
            assert_never(key)

    return so_far_keys


@dataclass
class YAMLDocument:
    """A dataclass to represent a YAML document in memory.

    Attributes:
        content: The content of the YAML document as a ruamel.yaml object.
    """

    content: YAMLLiteral
    roundtripper: ruamel.yaml.YAML


@contextmanager
def edit_yaml(
    yaml_path: Path,
    *,
    guess_indent: bool = True,
) -> Generator[YAMLDocument, None, None]:
    """A context manager to modify a YAML file in-place, with managed read and write."""
    with yaml_path.open(mode="r") as f:
        try:
            yaml_document = _get_yaml_document(f, guess_indent=guess_indent)
        except YAMLError as err:
            msg = f"Error reading '{yaml_path}':\n{err}"
            raise YAMLDecodeError(msg) from None
    yield yaml_document
    yaml_document.roundtripper.dump(yaml_document.content, stream=yaml_path)


def _get_yaml_document(
    _io: StringIO | TextIOWrapper, /, *, guess_indent: bool = True
) -> YAMLDocument:
    # Can't preserve quotes so don't keep the content.
    # Yes, it' not very efficient to load the content twice.
    try:
        content, sequence_ind, offset_ind = load_yaml_guess_indent(_io)
    except YAMLError as err:
        if "mapping values are not allowed here" in str(err):
            info_print("Hint: You may have incorrect indentation the YAML file.")
        raise err

    if not guess_indent:
        sequence_ind = None
        offset_ind = None

    if sequence_ind is None:
        sequence_ind = 4
    if offset_ind is None:
        offset_ind = 2

    yaml = ruamel.yaml.YAML(typ="rt")
    yaml.indent(mapping=sequence_ind, sequence=sequence_ind, offset=offset_ind)
    yaml.preserve_quotes = True

    yaml_document = YAMLDocument(content=content, roundtripper=yaml)
    return yaml_document
