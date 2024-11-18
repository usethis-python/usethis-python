from functools import singledispatch
from itertools import zip_longest

from pydantic import BaseModel, RootModel

type ModelLiteral = bool | int | float | str
type ModelRepresentation = (
    ModelLiteral
    | dict[str, "ModelRepresentation"]
    | list["ModelRepresentation"]
    | BaseModel
)


@singledispatch
def fancy_model_dump(
    model: BaseModel | ModelRepresentation,
    *,
    reference: ModelRepresentation | None = None,
    order_by_cls: dict[type[BaseModel], list[str]] | None = None,
) -> ModelRepresentation:
    # TODO docstring. N.B. in order_by_cls we ignore if a RootModel
    # Also note that if keys are missing from the order list, we will place them at the
    # end in the Model definition order.
    # Need to explain the point of reference is to minimize a diff
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
    for value, ref in zip_longest(model, reference, fillvalue=None):
        # TODO test the case where the zip longest aspect kicks in
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

    # TODO duplication with other dict-like handling?
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


# TODO reduce duplication, also above. Try to use variable ref to type
@fancy_model_dump.register(bool | int | float | str)
def _(
    model: ModelLiteral,
    *,
    reference: ModelRepresentation | None = None,
    order_by_cls: dict[type[BaseModel], list[str]] | None = None,
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
        default_value = model.model_fields[key].default

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
        # This is tehcnically a limitation in what kind of diffs we can express in
        # the dump but it's a relatively minor one.

        if value_ref is not None:
            ref_has_default = value_ref == default_value
        else:
            ref_has_default = False

        if (value == default_value) and not ref_has_default:
            continue

        d[key] = fancy_model_dump(value, reference=value_ref, order_by_cls=order_by_cls)

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
