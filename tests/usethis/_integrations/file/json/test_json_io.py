from pathlib import Path

import pytest

from usethis._integrations.file.json.errors import (
    JSONNotFoundError,
    UnexpectedJSONIOError,
    UnexpectedJSONOpenError,
)
from usethis._integrations.file.json.io_ import JSONFileManager
from usethis._test import change_cwd


class ExampleJSONFileManager(JSONFileManager):
    @property
    def relative_path(self) -> Path:
        """Return the relative path to the file."""
        return Path("example.json")


class TestJSONFileManager:
    class TestEnter:
        def test_double_open(self, tmp_path: Path):
            # Act, Assert
            with (
                change_cwd(tmp_path),
                ExampleJSONFileManager() as mgr,
                pytest.raises(UnexpectedJSONOpenError),
            ):
                mgr.__enter__()

    class TestReadFile:
        def test_success(self, tmp_path: Path):
            # Arrange
            (tmp_path / "example.json").write_text('{"key": "value"}')

            # Act, Assert
            with change_cwd(tmp_path), ExampleJSONFileManager() as mgr:
                mgr.read_file()

        def test_file_not_found(self, tmp_path: Path):
            # Act, Assert
            with (
                change_cwd(tmp_path),
                ExampleJSONFileManager() as mgr,
                pytest.raises(JSONNotFoundError),
            ):
                mgr.read_file()

        def test_no_context_manager(self, tmp_path: Path):
            # Act, Assert
            with (
                change_cwd(tmp_path),
                ExampleJSONFileManager() as mgr,
                pytest.raises(UnexpectedJSONIOError),
            ):
                mgr.read_file()
