"""Safer abstractions for Pydantic TypeAdapter validation.

This module provides two wrappers around `TypeAdapter.validate_python`
that guarantee every `ValidationError` is handled — either re-raised as
a caller-specified error or swallowed in favour of a default value.

Rationale: raw `pydantic.ValidationError` should never propagate out of
usethis.  By routing all validation through these helpers and banning
direct `TypeAdapter` usage via Ruff (TID251), we make unhandled
validation errors a lint failure rather than a runtime surprise.
"""

from __future__ import annotations

from typing import TypeVar, overload

from pydantic import TypeAdapter, ValidationError  # noqa: TID251

T = TypeVar("T")


@overload
def validate_or_raise(
    type_: type[T],
    obj: object,
    *,
    err: Exception,
) -> T: ...


@overload
def validate_or_raise(
    type_: object,
    obj: object,
    *,
    err: Exception,
) -> object: ...


def validate_or_raise(
    type_: object,
    obj: object,
    *,
    err: Exception,
) -> object:
    """Validate `obj` against `type_`, raising a custom error on failure.

    Args:
        type_: The target type to validate against (forwarded to
            `TypeAdapter`).
        obj: The object to validate.
        err: An instantiated exception to raise when validation fails.

    Returns:
        The validated (and possibly coerced) object.

    Raises:
        type(err): When `obj` does not conform to `type_`.
    """
    try:
        return TypeAdapter(type_).validate_python(obj)
    except ValidationError as ve:
        original_msg = err.args[0] if err.args else str(err)
        msg = f"{original_msg} ({ve})"
        raise type(err)(msg) from None


def validate_or_default(
    type_: object,
    obj: object,
    *,
    default: T,
    warn_msg: str | None = None,
) -> T:
    """Validate `obj` against `type_`, returning `default` on failure.

    Args:
        type_: The target type to validate against (forwarded to
            `TypeAdapter`).
        obj: The object to validate.
        default: The value to return when validation fails.
        warn_msg: An optional warning message to display to the user
            when validation fails.  When `None`, no warning is emitted.

    Returns:
        The validated object, or `default` if validation fails.
    """
    try:
        return TypeAdapter(type_).validate_python(obj)
    except ValidationError as ve:
        if warn_msg is not None:
            from usethis._console import warn_print  # noqa: PLC0415

            warn_print(f"{warn_msg} ({ve})")
        return default
