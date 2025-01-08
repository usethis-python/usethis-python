from usethis._integrations.bitbucket.schema import Step, Step1, Step2


def step1tostep(step1: Step1) -> Step:
    """Promoting Step1 to a standard Step.

    This is necessary because there is some unusual inconsistency in the JSON Schema
    for Bitbucket pipelines that means conditions are not constrained by type when
    occurring in a stage, whereas at time of writing they are constrained in all other
    circumstances. This gives rise to strange naming in the output of
    datamodel-code-generator (which is repeated here for consistency).
    """
    step2 = step1.step

    step = Step(**step2.model_dump())
    return step


def steptostep1(step: Step) -> Step1:
    """Demoting Step to a Step1.

    See `step1tostep` for more information.
    """
    step1 = Step1(step=Step2(**step.model_dump()))
    return step1
