from usethis._ci import (
    add_bitbucket_precommit_step,
    add_bitbucket_pytest_steps,
    is_bitbucket_used,
)
from usethis._console import box_print, info_print
from usethis._integrations.bitbucket.config import (
    add_bitbucket_pipeline_config,
    remove_bitbucket_pipeline_config,
)
from usethis._integrations.bitbucket.steps import (
    add_placeholder_step_in_default,
)
from usethis._tool import PreCommitTool, PytestTool


def use_ci_bitbucket(*, remove: bool = False) -> None:
    if not remove:
        if is_bitbucket_used():
            return

        add_bitbucket_pipeline_config()

        steps = []
        # TODO need a mechanism for removals if we run usethis tool pre-commit --remove
        if PreCommitTool().is_used():
            add_bitbucket_precommit_step()

        if PytestTool().is_used():
            add_bitbucket_pytest_steps()

        if not steps:
            add_placeholder_step_in_default()
            info_print(
                "Consider `usethis tool pytest` to start testing your code, including in the pipeline."
            )

        box_print("Run your first pipeline on the Bitbucket website.")
    else:
        remove_bitbucket_pipeline_config()
