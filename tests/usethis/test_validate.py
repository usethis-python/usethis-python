"""Tests for usethis._validate."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from usethis._validate import validate_or_default, validate_or_raise


class _CustomError(Exception):
    """Test error class."""


class TestValidateOrRaise:
    """Tests for validate_or_raise."""

    def test_valid_str(self):
        result = validate_or_raise(
            str, "hello", error_cls=_CustomError, error_msg="fail"
        )
        assert result == "hello"

    def test_valid_dict(self):
        result = validate_or_raise(
            dict, {"a": 1}, error_cls=_CustomError, error_msg="fail"
        )
        assert result == {"a": 1}

    def test_valid_list_str(self):
        result = validate_or_raise(
            list[str], ["a", "b"], error_cls=_CustomError, error_msg="fail"
        )
        assert result == ["a", "b"]

    def test_invalid_raises_custom_error(self):
        with pytest.raises(_CustomError, match="not a string"):
            validate_or_raise(
                str, 123, error_cls=_CustomError, error_msg="not a string"
            )

    def test_invalid_does_not_raise_validation_error(self):
        """Ensure pydantic.ValidationError does not propagate."""
        with pytest.raises(_CustomError):
            validate_or_raise(str, [1, 2, 3], error_cls=_CustomError, error_msg="bad")

        # Explicitly verify ValidationError is NOT raised
        try:
            validate_or_raise(str, [1, 2, 3], error_cls=_CustomError, error_msg="bad")
        except _CustomError:
            pass
        except ValidationError:
            pytest.fail("ValidationError should not propagate")

    def test_custom_error_msg_preserved(self):
        with pytest.raises(_CustomError, match=r"^my custom message$"):
            validate_or_raise(
                int, "not-an-int", error_cls=_CustomError, error_msg="my custom message"
            )

    def test_coercion(self):
        """TypeAdapter may coerce compatible types."""
        result = validate_or_raise(float, 1, error_cls=_CustomError, error_msg="fail")
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
