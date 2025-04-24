from __future__ import annotations

from pathlib import Path

from usethis._console import box_print
from usethis._integrations.ci.bitbucket.anchor import (
    ScriptItemAnchor as BitbucketScriptItemAnchor,
)
from usethis._integrations.ci.bitbucket.schema import Script as BitbucketScript
from usethis._integrations.ci.bitbucket.schema import Step as BitbucketStep
from usethis._integrations.uv.deps import (
    Dependency,
)
from usethis._integrations.uv.used import is_uv_used
from usethis._tool.base import Tool


class PreCommitTool(Tool):
    # https://github.com/pre-commit/pre-commit
    @property
    def name(self) -> str:
        return "pre-commit"

    def print_how_to_use(self) -> None:
        if is_uv_used():
            box_print(
                "Run 'uv run pre-commit run --all-files' to run the hooks manually."
            )
        else:
            box_print("Run 'pre-commit run --all-files' to run the hooks manually.")

    def get_dev_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        return [Dependency(name="pre-commit")]

    def get_managed_files(self) -> list[Path]:
        return [Path(".pre-commit-config.yaml")]

    def get_bitbucket_steps(self) -> list[BitbucketStep]:
        return [
            BitbucketStep(
                name=f"Run {self.name}",
                caches=["uv", "pre-commit"],
                script=BitbucketScript(
                    [
                        BitbucketScriptItemAnchor(name="install-uv"),
                        "uv run pre-commit run --all-files",
                    ]
                ),
            )
        ]
