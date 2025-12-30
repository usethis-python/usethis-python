from __future__ import annotations

from usethis._integrations.ci.bitbucket import schema


def step1tostep(step1: schema.Step1) -> schema.Step:
    """Promoting Step1 to a standard Step.

    This is necessary because there is some unusual inconsistency in the JSON Schema
    for Bitbucket Pipelines that means conditions are not constrained by type when
    occurring in a stage, whereas at time of writing they are constrained in all other
    circumstances. This gives rise to strange naming in the output of
    datamodel-code-generator (which is repeated here for consistency).
    """
    step2 = step1.step

    step = schema.Step(**step2.model_dump(by_alias=True))
    return step
