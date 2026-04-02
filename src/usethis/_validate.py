"""Safer abstractions for Pydantic TypeAdapter validation.

This module provides two wrappers around ``TypeAdapter.validate_python``
that guarantee every ``ValidationError`` is handled — either re-raised as
a caller-specified error or swallowed in favour of a default value.

Rationale: raw ``pydantic.ValidationError`` should never propagate out of
usethis.  By routing all validation through these helpers and banning
direct ``TypeAdapter`` usage via Ruff (TID251), we make unhandled
validation errors a lint failure rather than a runtime surprise.
"""

from __future__ import annotations

from typing import Any, TypeVar

from pydantic import TypeAdapter, ValidationError  # noqa: TID251

T = TypeVar("T")


def validate_or_raise(
    type_: Any,
    obj: object,
    *,
    error_cls: type[Exception],
    error_msg: str,
) -> Any:
    """Validate ``obj`` against ``type_``, raising a custom error on failure.

    Args:
        type_: The target type to validate against (forwarded to
            ``TypeAdapter``).
        obj: The object to validate.
        error_cls: The exception class to raise when validation fails.
        error_msg: The message for the raised exception.

    Returns:
        The validated (and possibly coerced) object.

    Raises:
        error_cls: When ``obj`` does not conform to ``type_``.
    """
    try:
        return TypeAdapter(type_).validate_python(obj)
    except ValidationError:
        raise error_cls(error_msg) from None


def validate_or_default(
    type_: Any,
    obj: object,
    *,
    default: T,
) -> T:
    """Validate ``obj`` against ``type_``, returning ``default`` on failure.

    Args:
        type_: The target type to validate against (forwarded to
            ``TypeAdapter``).
        obj: The object to validate.
        default: The value to return when validation fails.

    Returns:
        The validated object, or ``default`` if validation fails.
    """
    try:
        return TypeAdapter(type_).validate_python(obj)
    except ValidationError:
        return default
