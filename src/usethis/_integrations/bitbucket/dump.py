from usethis._integrations.bitbucket.pipeline import (
    PipelinesConfiguration,
    Step,
    Step2,
    StepBase,
)
from usethis._integrations.pydantic.dump import ModelRepresentation, fancy_model_dump

# TODO test RHS list values are all attributes of LHS
ORDER_BY_CLS = {
    PipelinesConfiguration: ["image", "clone", "definitions"],
    StepBase: ["name", "caches", "script"],
    Step: ["name", "caches", "script"],
    Step2: ["name", "caches", "script"],
}


def fancy_pipelines_model_dump(
    config: PipelinesConfiguration, *, reference: ModelRepresentation
) -> dict[str, ModelRepresentation]:
    dump = fancy_model_dump(config, reference=reference, order_by_cls=ORDER_BY_CLS)

    # TODO this feels a bit hacky, tidy up
    if not isinstance(dump, dict):
        msg = (
            f"Trying to represent Bitbucket pipelines configuration.\n"
            f"Expected dict, got {type(dump)}"
        )
        raise TypeError(msg)

    return dump
