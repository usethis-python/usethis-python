from pathlib import Path

from usethis._console import box_print, tick_print
from usethis._core.badge import add_pre_commit_badge, add_ruff_badge
from usethis._integrations.pyproject.errors import PyProjectTOMLError
from usethis._integrations.pyproject.name import get_description, get_name
from usethis._tool import PreCommitTool, RuffTool


def add_readme() -> None:
    """Add a README.md file to the project."""

    path = Path.cwd() / "README.md"

    if path.exists():
        return

    try:
        project_name = get_name()
    except PyProjectTOMLError:
        project_name = None

    try:
        project_description = get_description()
    except PyProjectTOMLError:
        project_description = None

    if project_name is not None and project_description is not None:
        content = f"""\
# {project_name}

{project_description}
"""
    elif project_name is not None:
        content = f"""\
# {project_name}
"""
    elif project_description is not None:
        content = f"""\
{project_description}
"""
    else:
        content = ""

    tick_print("Writing 'README.md'.")
    path.write_text(content)

    if RuffTool().is_used():
        add_ruff_badge()

    if PreCommitTool().is_used():
        add_pre_commit_badge()

    box_print("Populate 'README.md' to help users understand the project.")
