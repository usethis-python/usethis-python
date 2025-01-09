from usethis._ci import (
    add_bitbucket_pre_commit_step,
    add_bitbucket_pytest_steps,
)
from usethis._console import box_print, info_print
from usethis._integrations.bitbucket.config import (
    add_bitbucket_pipeline_config,
    remove_bitbucket_pipeline_config,
)
from usethis._tool import PreCommitTool, PytestTool


def use_ci_bitbucket(*, remove: bool = False) -> None:
    if not remove:
        use_pre_commit = PreCommitTool().is_used()
        use_pytest = PytestTool().is_used()
        use_any_tool = use_pre_commit or use_pytest

        add_bitbucket_pipeline_config(report_placeholder=not use_any_tool)

        if use_pre_commit:
            add_bitbucket_pre_commit_step()

        if use_pytest:
            add_bitbucket_pytest_steps()

        else:
            info_print(
                "Consider `usethis tool pytest` to test your code for the pipeline."
            )

        box_print("Run your pipeline via the Bitbucket website.")
    else:
        remove_bitbucket_pipeline_config()
