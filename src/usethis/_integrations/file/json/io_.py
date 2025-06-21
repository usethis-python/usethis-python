from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, TypeAlias

from usethis._integrations.file.json.errors import (
    JSONDecodeError,
    JSONNotFoundError,
    UnexpectedJSONIOError,
    UnexpectedJSONOpenError,
)
from usethis._io import (
    KeyValueFileManager,
    UnexpectedFileIOError,
    UnexpectedFileOpenError,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from typing_extensions import Self

    from usethis._io import Key

JSONDocument: TypeAlias = dict[str, Any]


class JSONFileManager(KeyValueFileManager):
    def __enter__(self) -> Self:
        try:
            return super().__enter__()
        except UnexpectedFileOpenError as err:
            raise UnexpectedJSONOpenError(err) from None

    def read_file(self) -> None:
        try:
            super().read_file()
        except FileNotFoundError as err:
            raise JSONNotFoundError(err) from None
        except UnexpectedFileIOError as err:
            raise UnexpectedJSONIOError(err) from None
        except json.JSONDecodeError as err:
            msg = f"Failed to decode '{self.name}': {err}"
            raise JSONDecodeError(msg) from None

    def _parse_content(self, content: str) -> JSONDocument:
        """Parse the content of the JSON file."""
        return json.loads(content)

    def __contains__(self, keys: Sequence[Key]) -> bool:
        """Check if a key exists in the JSON file."""
        raise NotImplementedError

    def __getitem__(self, keys: Sequence[Key]) -> Any:
        raise NotImplementedError

    def __delitem__(self, keys: Sequence[Key]) -> None:
        """Remove a value from the JSON file."""
        raise NotImplementedError

    def set_value(
        self, *, keys: Sequence[Key], value: Any, exists_ok: bool = False
    ) -> None:
        """Set a value in the JSON file."""
        raise NotImplementedError

    def extend_list(self, *, keys: Sequence[Key], values: list[Any]) -> None:
        """Extend a list in the JSON file."""
        raise NotImplementedError

    def remove_from_list(self, *, keys: Sequence[Key], values: list[Any]) -> None:
        """Remove values from a list in the JSON file."""
        raise NotImplementedError
