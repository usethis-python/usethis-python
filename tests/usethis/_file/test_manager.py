from pathlib import Path

from typing_extensions import override

from usethis._file.manager import Document, FileManager
from usethis._test import change_cwd


class TestUsethisFileManager:
    class TestContent:
        def test_setter(self, tmp_path: Path) -> None:
            # Arrange
            class MyUsethisFileManager(FileManager[Document]):
                @property
                @override
                def relative_path(self) -> Path:
                    return Path("pyproject.toml")

                @override
                def _dump_content(self) -> str:
                    raise NotImplementedError

                @override
                def _parse_content(self, content: str) -> None:
                    raise NotImplementedError

            with change_cwd(tmp_path):
                manager = MyUsethisFileManager()

            # Act
            manager._content = 42

            # Assert
            assert manager._content == 42

    class TestEq:
        def test_example(self) -> None:
            # Arrange
            class MyUsethisFileManager(FileManager[Document]):
                @property
                @override
                def relative_path(self) -> Path:
                    return Path("pyproject.toml")

                @override
                def _dump_content(self) -> str:
                    raise NotImplementedError

                @override
                def _parse_content(self, content: str) -> None:
                    raise NotImplementedError

            manager = MyUsethisFileManager()
            other_manager = MyUsethisFileManager()

            # Act
            result = manager == other_manager

            # Assert
            assert result is True

        def test_different_type(self) -> None:
            # Arrange
            class MyUsethisFileManager(FileManager[Document]):
                @property
                @override
                def relative_path(self) -> Path:
                    return Path("pyproject.toml")

                @override
                def _dump_content(self) -> str:
                    raise NotImplementedError

                @override
                def _parse_content(self, content: str) -> None:
                    raise NotImplementedError

            manager = MyUsethisFileManager()
            other_manager = object()

            # Act
            result = manager == other_manager

            # Assert
            assert result is False

    class TestRepr:
        def test_example(self, tmp_path: Path) -> None:
            # Arrange
            class MyUsethisFileManager(FileManager[Document]):
                @property
                @override
                def relative_path(self) -> Path:
                    return Path("pyproject.toml")

                @override
                def _dump_content(self) -> str:
                    raise NotImplementedError

                @override
                def _parse_content(self, content: str) -> None:
                    raise NotImplementedError

            with change_cwd(tmp_path):
                manager = MyUsethisFileManager()

            # Act
            repr_str = repr(manager)

            # Assert
            assert repr_str == "MyUsethisFileManager('pyproject.toml')"
