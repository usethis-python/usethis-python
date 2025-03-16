from pathlib import Path

import pytest

from usethis._integrations.file.toml.io_ import TOMLFileManager
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

    class TestSetValue:
        def test_no_keys_raises(self, tmp_path: Path) -> None:
            # Arrange
            class MyTOMLFileManager(TOMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("pyproject.toml")

            with change_cwd(tmp_path):
                manager = MyTOMLFileManager()

            # Act, Assert
            with pytest.raises(
                ValueError, match="At least one ID key must be provided."
            ):
                manager.set_value(keys=[], value="d")

        def test_inplace_modifications(self, tmp_path: Path) -> None:
            # Arrange
            class MyTOMLFileManager(TOMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("pyproject.toml")

            with change_cwd(tmp_path), MyTOMLFileManager() as manager:
                (tmp_path / "pyproject.toml").touch()

                manager[["a"]] = "b"

                original = manager._content

                # Act
                manager.set_value(keys=["c"], value="d")

                # Assert
                assert manager._content != original

    class TestDel:
        def test_no_keys_raises(self, tmp_path: Path) -> None:
            # Arrange
            class MyTOMLFileManager(TOMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("pyproject.toml")

            with change_cwd(tmp_path), MyTOMLFileManager() as manager:
                (tmp_path / "pyproject.toml").touch()

                # Act, Assert
                with pytest.raises(
                    ValueError, match="At least one ID key must be provided."
                ):
                    del manager[[]]

        def test_inplace_modifications(self, tmp_path: Path) -> None:
            # Arrange
            class MyTOMLFileManager(TOMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("pyproject.toml")

            with change_cwd(tmp_path), MyTOMLFileManager() as manager:
                (tmp_path / "pyproject.toml").touch()

                manager[["a"]] = "b"
                original = manager._content

                # Act
                del manager[["a"]]

                # Assert
                assert manager._content != original

    class TestExtendList:
        def test_inplace_modifications(self, tmp_path: Path) -> None:
            # Arrange
            class MyTOMLFileManager(TOMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("pyproject.toml")

            with change_cwd(tmp_path), MyTOMLFileManager() as manager:
                (tmp_path / "pyproject.toml").touch()

                manager[["a"]] = ["b", "c"]

                # Act
                manager.extend_list(keys=["a"], values=["d"])

                # Assert
                assert manager._content == {"a": ["b", "c", "d"]}

        def test_no_keys_raises(self, tmp_path: Path) -> None:
            # Arrange
            class MyTOMLFileManager(TOMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("pyproject.toml")

            with change_cwd(tmp_path), MyTOMLFileManager() as manager:
                (tmp_path / "pyproject.toml").touch()

                # Act, Assert
                with pytest.raises(
                    ValueError, match="At least one ID key must be provided."
                ):
                    manager.extend_list(keys=[], values=["d"])

    class TestRemoveFromList:
        def test_inplace_modifications(self, tmp_path: Path) -> None:
            # Arrange
            class MyTOMLFileManager(TOMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("pyproject.toml")

            with change_cwd(tmp_path), MyTOMLFileManager() as manager:
                (tmp_path / "pyproject.toml").touch()

                manager[["a"]] = ["b", "c", "d"]

                # Act
                manager.remove_from_list(keys=["a"], values=["c"])

                # Assert
                assert manager._content == {"a": ["b", "d"]}

        def test_no_keys_raises(self, tmp_path: Path) -> None:
            # Arrange
            class MyTOMLFileManager(TOMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("pyproject.toml")

            with change_cwd(tmp_path), MyTOMLFileManager() as manager:
                (tmp_path / "pyproject.toml").touch()

                # Act, Assert
                with pytest.raises(
                    ValueError, match="At least one ID key must be provided."
                ):
                    manager.remove_from_list(keys=[], values=["d"])

        def test_already_not_present(self, tmp_path: Path) -> None:
            # Arrange
            class MyTOMLFileManager(TOMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("pyproject.toml")

            with change_cwd(tmp_path), MyTOMLFileManager() as manager:
                (tmp_path / "pyproject.toml").touch()

                manager[["b"]] = ["c"]

                original = manager._content

                # Act
                manager.remove_from_list(keys=["a"], values=["d"])

                # Assert
                assert manager._content == original

    class TestGetItem:
        def test_no_keys_raises(self, tmp_path: Path) -> None:
            # Arrange
            class MyTOMLFileManager(TOMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("pyproject.toml")

            with change_cwd(tmp_path), MyTOMLFileManager() as manager:
                (tmp_path / "pyproject.toml").touch()

                # Act, Assert
                with pytest.raises(
                    ValueError, match="At least one ID key must be provided."
                ):
                    manager[[]]
