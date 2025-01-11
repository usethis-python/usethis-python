from pathlib import Path

from usethis._console import box_print, tick_print
from usethis._integrations.pyproject.errors import PyProjectTOMLError
from usethis._integrations.pyproject.name import get_description, get_name


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
    box_print("Populate 'README.md' to help users understand the project.")
