from pathlib import Path

import pytest

from usethis._integrations.toml.io_ import TOMLFileManager
from usethis._test import change_cwd


class TestTOMLFileManager:
    class TestDumpContent:
        def test_no_content(self, tmp_path: Path) -> None:
            # Arrange
            class MyTOMLFileManager(TOMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("pyproject.toml")

            with change_cwd(tmp_path):
                manager = MyTOMLFileManager()

            # Act, Assert
            with pytest.raises(ValueError, match="Content is None, cannot dump."):
                manager._dump_content()

    class TestContent:
        def test_content_setter(self, tmp_path: Path) -> None:
            # Arrange
            class MyTOMLFileManager(TOMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("pyproject.toml")

            with change_cwd(tmp_path):
                manager = MyTOMLFileManager()

            # Act
            manager._content = 42  # type: ignore

            # Assert
            assert manager._content == 42
