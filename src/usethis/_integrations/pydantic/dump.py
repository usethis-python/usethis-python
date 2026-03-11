from __future__ import annotations

from itertools import zip_longest
from typing import TYPE_CHECKING

from pydantic import BaseModel, RootModel

if TYPE_CHECKING:
    from usethis._integrations.pydantic.typing_ import ModelRepresentation


class _FillValue:
    pass


_FILL_VALUE = _FillValue()


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
    if isinstance(model, list):
        return _fancy_model_dump_list(model, reference=reference, order_by_cls=order_by_cls)
    elif isinstance(model, dict):
        return _fancy_model_dump_dict(model, reference=reference, order_by_cls=order_by_cls)
    elif isinstance(model, bool | int | float | str):
        return model
    elif isinstance(model, RootModel):
        return fancy_model_dump(model.root, reference=reference, order_by_cls=order_by_cls)
    elif isinstance(model, BaseModel):
        return _fancy_model_dump_base_model(
            model, reference=reference, order_by_cls=order_by_cls
        )
    else:
        return model


def _fancy_model_dump_list(
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


def _fancy_model_dump_dict(
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


def _fancy_model_dump_base_model(
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

        # The value for the reference (for recursion)
        value_ref = _get_value_ref(reference, key=key)

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


def _get_value_ref(
    reference: ModelRepresentation | None, *, key: str
) -> ModelRepresentation | None:
    # The reference for the value (for recursion)
    if isinstance(reference, dict | BaseModel):
        try:
            value_ref = dict(reference)[key]  # ty: ignore[no-matching-overload]
        except KeyError:
            value_ref = None
    else:
        value_ref = None

    return value_ref
