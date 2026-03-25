from __future__ import annotations

from typing import final

from typing_extensions import override

from usethis._console import how_print
from usethis._detect.pre_commit import is_pre_commit_used
from usethis._tool.base import Tool
from usethis._tool.impl.spec.pre_commit import PreCommitToolSpec


@final
class PreCommitTool(PreCommitToolSpec, Tool):
    @override
    def is_used(self) -> bool:
        return is_pre_commit_used()

    @override
    def print_how_to_use(self) -> None:
        how_print(f"Run '{self.how_to_use_cmd()}' to run the hooks manually.")

    @override
    def migrate_config_to_pre_commit(self) -> None:
        pass

    @override
    def migrate_config_from_pre_commit(self) -> None:
        pass
