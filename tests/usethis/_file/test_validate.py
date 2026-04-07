"""Tests for usethis._file.validate."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from _test import change_cwd
from usethis._config_file import files_manager
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._file.validate import validate_or_default, validate_or_raise


class _CustomError(Exception):
    """Test error class."""


class TestValidateOrRaise:
    """Tests for validate_or_raise."""

    def test_valid_str(self):
        result = validate_or_raise(str, "hello", err=_CustomError("fail"))
        assert result == "hello"

    def test_valid_dict(self):
        result = validate_or_raise(dict, {"a": 1}, err=_CustomError("fail"))
        assert result == {"a": 1}

    def test_valid_list_str(self):
        result = validate_or_raise(list[str], ["a", "b"], err=_CustomError("fail"))
        assert result == ["a", "b"]

    def test_invalid_raises_custom_error(self):
        with pytest.raises(_CustomError, match="not a string"):
            validate_or_raise(str, 123, err=_CustomError("not a string"))

    def test_invalid_does_not_raise_validation_error(self):
        """Ensure pydantic.ValidationError does not propagate."""
        with pytest.raises(_CustomError):
            validate_or_raise(str, [1, 2, 3], err=_CustomError("bad"))

        # Explicitly verify ValidationError is NOT raised
        try:
            validate_or_raise(str, [1, 2, 3], err=_CustomError("bad"))
        except _CustomError:
            pass
        except ValidationError:
            pytest.fail("ValidationError should not propagate")

    def test_custom_error_msg_preserved(self):
        with pytest.raises(_CustomError, match=r"^my custom message$"):
            validate_or_raise(int, "not-an-int", err=_CustomError("my custom message"))

    def test_coercion(self):
        """TypeAdapter may coerce compatible types."""
        result = validate_or_raise(float, 1, err=_CustomError("fail"))
        assert result == 1.0
        assert isinstance(result, float)


class TestValidateOrDefault:
    """Tests for validate_or_default."""

    def test_valid_returns_value(self):
        result = validate_or_default(str, "hello", default="fallback")
        assert result == "hello"

    def test_valid_dict(self):
        result = validate_or_default(dict, {"a": 1}, default={})
        assert result == {"a": 1}

    def test_valid_list_str(self):
        result = validate_or_default(list[str], ["a", "b"], default=[])
        assert result == ["a", "b"]

    def test_invalid_returns_default(self):
        result = validate_or_default(str, 123, default="fallback")
        assert result == "fallback"

    def test_invalid_returns_empty_list_default(self):
        result = validate_or_default(list[str], "not-a-list", default=[])
        assert result == []

    def test_invalid_returns_none_default(self):
        result = validate_or_default(str, [1, 2, 3], default=None)
        assert result is None

    def test_invalid_returns_false_default(self):
        result = validate_or_default(bool, "not-a-bool", default=False)
        assert result is False

    def test_does_not_raise_validation_error(self):
        """Ensure pydantic.ValidationError does not propagate."""
        try:
            validate_or_default(str, [1, 2, 3], default="safe")
        except ValidationError:
            pytest.fail("ValidationError should not propagate")

    def test_coercion(self):
        """TypeAdapter may coerce compatible types."""
        result = validate_or_default(float, 1, default=0.0)
        assert result == 1.0
        assert isinstance(result, float)

    def test_warn_msg_emitted_on_failure(self, capfd: pytest.CaptureFixture[str]):
        result = validate_or_default(
            str, 123, default="fallback", warn_msg="bad value found"
        )
        assert result == "fallback"
        captured = capfd.readouterr()
        assert "bad value found" in captured.out

    def test_warn_msg_not_emitted_on_success(self, capfd: pytest.CaptureFixture[str]):
        result = validate_or_default(
            str, "hello", default="fallback", warn_msg="should not appear"
        )
        assert result == "hello"
        captured = capfd.readouterr()
        assert "should not appear" not in captured.out

    def test_no_warn_msg_by_default(self, capfd: pytest.CaptureFixture[str]):
        result = validate_or_default(str, 123, default="fallback")
        assert result == "fallback"
        captured = capfd.readouterr()
        assert captured.out == ""


class TestGetValidated:
    """Tests for KeyValueFileManager.validated_get."""

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
    """Tests for KeyValueFileManager.ensure_get."""

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
