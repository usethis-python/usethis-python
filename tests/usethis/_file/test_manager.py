from pathlib import Path

import pytest
from typing_extensions import override

from _test import change_cwd
from usethis._config_file import files_manager
from usethis._file.manager import Document, FileManager
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager


class _CustomError(Exception):
    pass


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


class TestKeyValueFileManager:
    class TestValidatedGet:
        def test_returns_validated_value(self, tmp_path: Path):
            (tmp_path / "pyproject.toml").write_text(
                '[project]\nname = "test"\nversion = "0.1.0"\n'
            )
            with change_cwd(tmp_path), files_manager():
                result = PyprojectTOMLManager().validated_get(
                    ["project", "name"], default="fallback", validate=str
                )
            assert result == "test"

        def test_returns_default_on_missing_key(self, tmp_path: Path):
            (tmp_path / "pyproject.toml").write_text(
                '[project]\nname = "test"\nversion = "0.1.0"\n'
            )
            with change_cwd(tmp_path), files_manager():
                result = PyprojectTOMLManager().validated_get(
                    ["project", "missing"], default="fallback", validate=str
                )
            assert result == "fallback"

        def test_returns_default_on_missing_file(self, tmp_path: Path):
            with change_cwd(tmp_path), files_manager():
                result = PyprojectTOMLManager().validated_get(
                    ["project", "name"], default="fallback", validate=str
                )
            assert result == "fallback"

        def test_returns_default_on_validation_failure(self, tmp_path: Path):
            (tmp_path / "pyproject.toml").write_text(
                '[project]\nname = "test"\nversion = "0.1.0"\nclassifiers = "not-a-list"\n'
            )
            with change_cwd(tmp_path), files_manager():
                result = PyprojectTOMLManager().validated_get(
                    ["project", "classifiers"], default=[], validate=list[str]
                )
            assert result == []

        def test_no_validation(self, tmp_path: Path):
            (tmp_path / "pyproject.toml").write_text(
                '[project]\nname = "test"\nversion = "0.1.0"\n'
            )
            with change_cwd(tmp_path), files_manager():
                result = PyprojectTOMLManager().validated_get(
                    ["project", "name"], default="fallback"
                )
            assert result == "test"

        def test_warn_msg_emitted_on_validation_failure(
            self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
        ):
            (tmp_path / "pyproject.toml").write_text(
                '[project]\nname = "test"\nversion = "0.1.0"\nclassifiers = "not-a-list"\n'
            )
            with change_cwd(tmp_path), files_manager():
                result = PyprojectTOMLManager().validated_get(
                    ["project", "classifiers"],
                    default=[],
                    validate=list[str],
                    warn_msg="invalid classifiers",
                )
            assert result == []
            captured = capfd.readouterr()
            assert "invalid classifiers" in captured.out

        def test_warn_msg_not_emitted_on_missing_key(
            self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
        ):
            (tmp_path / "pyproject.toml").write_text(
                '[project]\nname = "test"\nversion = "0.1.0"\n'
            )
            with change_cwd(tmp_path), files_manager():
                result = PyprojectTOMLManager().validated_get(
                    ["project", "missing"],
                    default="fallback",
                    validate=str,
                    warn_msg="should not appear",
                )
            assert result == "fallback"
            captured = capfd.readouterr()
            assert "should not appear" not in captured.out

    class TestEnsureGet:
        def test_returns_validated_value(self, tmp_path: Path):
            (tmp_path / "pyproject.toml").write_text(
                '[project]\nname = "test"\nversion = "0.1.0"\n'
            )
            with change_cwd(tmp_path), files_manager():
                result = PyprojectTOMLManager().ensure_get(
                    ["project", "name"],
                    err=_CustomError("missing"),
                    validate=str,
                )
            assert result == "test"

        def test_raises_on_missing_key(self, tmp_path: Path):
            (tmp_path / "pyproject.toml").write_text(
                '[project]\nname = "test"\nversion = "0.1.0"\n'
            )
            with (
                change_cwd(tmp_path),
                files_manager(),
                pytest.raises(_CustomError, match="missing"),
            ):
                PyprojectTOMLManager().ensure_get(
                    ["project", "missing"],
                    err=_CustomError("missing"),
                    validate=str,
                )

        def test_raises_on_missing_file(self, tmp_path: Path):
            with (
                change_cwd(tmp_path),
                files_manager(),
                pytest.raises(_CustomError, match="no file"),
            ):
                PyprojectTOMLManager().ensure_get(
                    ["project", "name"],
                    err=_CustomError("no file"),
                    validate=str,
                )

        def test_raises_on_validation_failure(self, tmp_path: Path):
            (tmp_path / "pyproject.toml").write_text(
                '[project]\nname = "test"\nversion = "0.1.0"\nclassifiers = "not-a-list"\n'
            )
            with (
                change_cwd(tmp_path),
                files_manager(),
                pytest.raises(_CustomError, match="bad type"),
            ):
                PyprojectTOMLManager().ensure_get(
                    ["project", "classifiers"],
                    err=_CustomError("bad type"),
                    validate=list[str],
                )
