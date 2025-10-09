from __future__ import annotations

from functools import singledispatch
from itertools import zip_longest
from typing import TYPE_CHECKING

from pydantic import BaseModel, RootModel

if TYPE_CHECKING:
    from typing import TypeAlias

    ModelLiteral: TypeAlias = bool | int | float | str
    ModelRepresentation: TypeAlias = (
        ModelLiteral
        | dict[str, "ModelRepresentation"]
        | list["ModelRepresentation"]
        | BaseModel
    )


class _FillValue:
    pass


_FILL_VALUE = _FillValue()


@singledispatch
def fancy_model_dump(
    model: BaseModel | ModelRepresentation,
    *,
    reference: ModelRepresentation | None = None,
    order_by_cls: dict[type[BaseModel], list[str]] | None = None,
) -> ModelRepresentation:
    """Like ``pydantic.model_dump`` but with bespoke formatting options.

    Args:
        model: The model to dump. This can be a pydantic model or a representation of
               the model (dict, list, etc.).
        reference: A representation to minimize the diff against. For example, if you
                   have a previous model_dump output and it contains default fields,
                   these will continue be included. If it omits default fields, these
                   will be omitted.
        order_by_cls: A lookup for different pydantic models, allowing each model's
                      fields to be forced to occur in a specific order in the output.
                      Unspecified fields will be placed at the end, in model definition
                      order. RootModels are ignored.
    """
    ...


@fancy_model_dump.register(list)
def _(
    model: list[BaseModel | ModelRepresentation],
    *,
    reference: ModelRepresentation | None = None,
    order_by_cls: dict[type[BaseModel], list[str]] | None = None,
) -> ModelRepresentation:
    if order_by_cls is None:
        order_by_cls = {}

    if reference is None:
        reference = []
    if not isinstance(reference, list):
        reference = []

    x = []
    for value, ref in zip_longest(model, reference, fillvalue=_FILL_VALUE):
        if value is _FILL_VALUE:
            # we've exhausted all the content.
            break
        if ref is _FILL_VALUE:
            # there's still content but nothing to compare it against
            ref = None

        # We don't use None as the fillvalue because it could be confused with the
        # case where the content itself is None.
        dump = fancy_model_dump(value, reference=ref, order_by_cls=order_by_cls)
        x.append(dump)
    return x


@fancy_model_dump.register(dict)
def _(
    model: dict[str, BaseModel | ModelRepresentation],
    *,
    reference: ModelRepresentation | None = None,
    order_by_cls: dict[type[BaseModel], list[str]] | None = None,
) -> ModelRepresentation:
    if order_by_cls is None:
        order_by_cls = {}
    d = {}
    for key, value in model.items():
        if reference is None:
            value_ref = None
        elif isinstance(reference, dict | BaseModel):
            try:
                value_ref = dict(reference)[key]
            except (KeyError, TypeError):
                value_ref = None
        else:
            value_ref = None

        d[key] = fancy_model_dump(value, reference=value_ref, order_by_cls=order_by_cls)

    return d


# N.B. when Python 3.10 support is dropped, we can register unions of types, rather than
# having these separate identical implementations for each type.
@fancy_model_dump.register(bool)
def _(
    model: ModelLiteral,
    *,
    reference: ModelRepresentation | None = None,  # noqa: ARG001
    order_by_cls: dict[type[BaseModel], list[str]] | None = None,  # noqa: ARG001
) -> ModelLiteral:
    return model


@fancy_model_dump.register(int)
def _(
    model: ModelLiteral,
    *,
    reference: ModelRepresentation | None = None,  # noqa: ARG001
    order_by_cls: dict[type[BaseModel], list[str]] | None = None,  # noqa: ARG001
) -> ModelLiteral:
    return model


@fancy_model_dump.register(float)
def _(
    model: ModelLiteral,
    *,
    reference: ModelRepresentation | None = None,  # noqa: ARG001
    order_by_cls: dict[type[BaseModel], list[str]] | None = None,  # noqa: ARG001
) -> ModelLiteral:
    return model


@fancy_model_dump.register(str)
def _(
    model: ModelLiteral,
    *,
    reference: ModelRepresentation | None = None,  # noqa: ARG001
    order_by_cls: dict[type[BaseModel], list[str]] | None = None,  # noqa: ARG001
) -> ModelLiteral:
    return model


@fancy_model_dump.register(RootModel)
def _(
    model: RootModel,
    *,
    reference: ModelRepresentation | None = None,
    order_by_cls: dict[type[BaseModel], list[str]] | None = None,
) -> ModelRepresentation:
    return fancy_model_dump(model.root, reference=reference, order_by_cls=order_by_cls)


@fancy_model_dump.register(BaseModel)
def _(
    model: BaseModel,
    *,
    reference: ModelRepresentation | None = None,
    order_by_cls: dict[type[BaseModel], list[str]] | None = None,
) -> ModelRepresentation:
    if order_by_cls is None:
        order_by_cls = {}

    d = {}
    for key, value in model:
        default_value = model.__class__.model_fields[key].default

        # The reference for the value (for recursion)
        if isinstance(reference, dict | BaseModel):
            try:
                value_ref = dict(reference)[key]
            except KeyError:
                value_ref = None
        else:
            value_ref = None

        # If the model has default value, we usually won't dump it.
        # There is an exception though: if we have a reference which we are trying
        # to minimize the diff against, then if the diff includes the default
        # explicitly, we should include it too.
        # This is technically a limitation in what kind of diffs we can express in
        # the dump but it's a relatively minor one.

        if value_ref is not None:
            ref_has_default = value_ref == default_value
        else:
            ref_has_default = False

        if (value == default_value) and not ref_has_default:
            continue

        # Find the key for display - there might be an alias
        display_key = model.__class__.model_fields[key].alias
        if display_key is None:
            display_key = key

        d[display_key] = fancy_model_dump(
            value, reference=value_ref, order_by_cls=order_by_cls
        )

    try:
        order = order_by_cls[type(model)]
    except KeyError:
        return d

    ordered_d = {}
    for key in order:
        if key in d:
            ordered_d[key] = d.pop(key)
    ordered_d.update(d)

    return ordered_d
