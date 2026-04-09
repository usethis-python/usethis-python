from __future__ import annotations

import pytest
from pydantic import ValidationError

from usethis._file.validate import validate_or_default, validate_or_raise


class _CustomError(Exception):
    pass


class TestValidateOrRaise:
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
        with pytest.raises(_CustomError, match="my custom message"):
            validate_or_raise(int, "not-an-int", err=_CustomError("my custom message"))

    def test_validation_details_injected(self):
        with pytest.raises(_CustomError, match="validation error") as exc_info:
            validate_or_raise(str, 123, err=_CustomError("bad type"))
        assert "bad type" in str(exc_info.value)

    def test_coercion(self):
        result = validate_or_raise(float, 1, err=_CustomError("fail"))
        assert result == 1.0
        assert isinstance(result, float)


class TestValidateOrDefault:
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
        try:
            validate_or_default(str, [1, 2, 3], default="safe")
        except ValidationError:
            pytest.fail("ValidationError should not propagate")

    def test_coercion(self):
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
        assert "validation error" in captured.out

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
