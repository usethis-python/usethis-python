from usethis import console
from usethis._pre_commit.hooks import get_hook_entry
from usethis._tool import PreCommitTool


def add_deptry_root_dir() -> None:
    if not PreCommitTool().is_used():
        return

    entry = get_hook_entry()
    if not entry.startswith("uv run --frozen deptry"):
        console.print(
            "☐ Reconfigure deptry in '.pre-commit-config.yaml' to run on the '/tests' directory.",
            style="blue",
        )
        return
