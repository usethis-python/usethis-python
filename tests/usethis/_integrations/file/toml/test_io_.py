from pathlib import Path

import pytest

from usethis._integrations.file.toml.errors import TOMLValueAlreadySetError
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

    class TestContains:
        def test_no_keys(self, tmp_path: Path) -> None:
            # Arrange
            class MyTOMLFileManager(TOMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("pyproject.toml")

            (tmp_path / "pyproject.toml").touch()

            # Act, Assert
            with change_cwd(tmp_path), MyTOMLFileManager() as manager:
                assert [] in manager

    class TestGetItem:
        def test_no_keys(self, tmp_path: Path) -> None:
            # Arrange
            class MyTOMLFileManager(TOMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("pyproject.toml")

            (tmp_path / "pyproject.toml").write_text("""\
[tool.usethis]
a = "b"
""")

            # Act, Assert
            with change_cwd(tmp_path), MyTOMLFileManager() as manager:
                assert manager[[]] == {"tool": {"usethis": {"a": "b"}}}

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
        def test_no_keys(self, tmp_path: Path) -> None:
            # Arrange
            class MyTOMLFileManager(TOMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("pyproject.toml")

            (tmp_path / "pyproject.toml").touch()

            # Act
            with change_cwd(tmp_path), MyTOMLFileManager() as manager:
                manager.set_value(keys=[], value={"b": "c"})

                # Assert
                assert manager._content == {"b": "c"}

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

        def test_root_level_already_set_raise(self, tmp_path: Path) -> None:
            # Arrange
            class MyTOMLFileManager(TOMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("pyproject.toml")

            with change_cwd(tmp_path), MyTOMLFileManager() as manager:
                (tmp_path / "pyproject.toml").touch()

                manager[["a"]] = "b"

                # Act, Assert
                with pytest.raises(
                    TOMLValueAlreadySetError,
                    match="Configuration value is at root level is already set.",
                ):
                    manager.set_value(keys=[], value={"a": "c"}, exists_ok=False)

        def test_root_level_already_set_no_raise(self, tmp_path: Path) -> None:
            # Arrange
            class MyTOMLFileManager(TOMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("pyproject.toml")

            with change_cwd(tmp_path), MyTOMLFileManager() as manager:
                (tmp_path / "pyproject.toml").touch()

                manager[["a"]] = "b"

                # Act
                manager.set_value(keys=[], value={"a": "c"}, exists_ok=True)

                # Assert
                assert manager._content == {"a": "c"}

        def test_set_list(self, tmp_path: Path) -> None:
            # Arrange
            class MyTOMLFileManager(TOMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("pyproject.toml")

            with change_cwd(tmp_path), MyTOMLFileManager() as manager:
                (tmp_path / "pyproject.toml").touch()

                # Act
                manager.set_value(keys=["a"], value=["b", "c"])

                # Assert
                assert manager._content == {"a": ["b", "c"]}

        def test_set_list_overwrite(self, tmp_path: Path) -> None:
            # Arrange
            class MyTOMLFileManager(TOMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("pyproject.toml")

            with change_cwd(tmp_path), MyTOMLFileManager() as manager:
                (tmp_path / "pyproject.toml").touch()

                manager[["a"]] = ["b", "c"]

                # Act, Assert
                with pytest.raises(
                    TOMLValueAlreadySetError,
                    match="Configuration value 'a' is already set.",
                ):
                    manager.set_value(keys=["a"], value=["d"])

    class TestDel:
        def test_no_keys(self, tmp_path: Path) -> None:
            # Arrange
            class MyTOMLFileManager(TOMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("pyproject.toml")

            with change_cwd(tmp_path), MyTOMLFileManager() as manager:
                (tmp_path / "pyproject.toml").touch()

                # Act
                del manager[[]]

            # Assert
            assert not manager._content

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

        def test_removing_root_level(self, tmp_path: Path) -> None:
            # Arrange
            class MyTOMLFileManager(TOMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("pyproject.toml")

            with change_cwd(tmp_path), MyTOMLFileManager() as manager:
                (tmp_path / "pyproject.toml").touch()

                manager[["a"]] = "b"

                # Act
                del manager[[]]

                # Assert
                assert not manager._content

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

        def test_doesnt_exist_yet(self, tmp_path: Path) -> None:
            # Arrange
            class MyTOMLFileManager(TOMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("pyproject.toml")

            with change_cwd(tmp_path), MyTOMLFileManager() as manager:
                (tmp_path / "pyproject.toml").touch()

                # Act
                manager.extend_list(keys=["a"], values=["b"])

                # Assert
                assert manager._content == {"a": ["b"]}

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

        def test_key_not_present(self, tmp_path: Path) -> None:
            # Arrange
            class MyTOMLFileManager(TOMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("pyproject.toml")

            with change_cwd(tmp_path), MyTOMLFileManager() as manager:
                (tmp_path / "pyproject.toml").touch()

                manager[["a"]] = ["b", "c"]

                # Act
                manager.remove_from_list(keys=["d"], values=["e"])

                # Assert
                assert manager._content == {"a": ["b", "c"]}
