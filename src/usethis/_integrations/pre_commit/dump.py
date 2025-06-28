from __future__ import annotations

from typing import TYPE_CHECKING

from usethis._integrations.pydantic.dump import fancy_model_dump

if TYPE_CHECKING:
    from pydantic import BaseModel

    from usethis._integrations.pre_commit.schema import JsonSchemaForPreCommitConfigYaml
    from usethis._integrations.pydantic.dump import ModelRepresentation

ORDER_BY_CLS: dict[type[BaseModel], list[str]] = {}


def pre_commit_fancy_dump(
    config: JsonSchemaForPreCommitConfigYaml, *, reference: ModelRepresentation
) -> dict[str, ModelRepresentation]:
    dump = fancy_model_dump(config, reference=reference, order_by_cls=ORDER_BY_CLS)

    if not isinstance(dump, dict):
        msg = (
            f"Invalid '{type(config)}' representation when dumping; expected dict, got "
            f"'{type(dump)}'."
        )
        raise TypeError(msg)

    return dump
