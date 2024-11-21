from pydantic import BaseModel

from usethis._integrations.bitbucket.pipeline import (
    PipelinesConfiguration,
    Step,
    Step2,
    StepBase,
)
from usethis._integrations.pydantic.dump import ModelRepresentation, fancy_model_dump

ORDER_BY_CLS: dict[type[BaseModel], list[str]] = {
    PipelinesConfiguration: ["image", "clone", "definitions"],
    StepBase: ["name", "caches", "script"],
    Step: ["name", "caches", "script"],
    Step2: ["name", "caches", "script"],
}


def fancy_pipelines_model_dump(
    config: PipelinesConfiguration, *, reference: ModelRepresentation
) -> dict[str, ModelRepresentation]:
    # TODO should test this function; by extension we should be testing ORDER_BY_CLS
    dump = fancy_model_dump(config, reference=reference, order_by_cls=ORDER_BY_CLS)

    if not isinstance(dump, dict):
        msg = (
            f"Trying to represent Bitbucket pipelines configuration.\n"
            f"Expected dict, got {type(dump)}"
        )
        raise TypeError(msg)

    return dump
