from __future__ import annotations

from usethis._config import usethis_config
from usethis._console import how_print, tick_print
from usethis._file.pyproject_toml.errors import PyprojectTOMLError
from usethis._file.pyproject_toml.name import get_description
from usethis._integrations.project.name import get_project_name
from usethis._integrations.readme.path import get_readme_path


def add_readme() -> None:
    """Add a README.md file to the project."""
    # Any file extension is fine, but we'll use '.md' for consistency.

    try:
        path = get_readme_path()
    except FileNotFoundError:
        pass
    else:
        # Check if the file is non-empty; if so, we will exit early
        try:
            existing_content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return
        if existing_content.strip():
            return

    project_name = get_project_name()

    try:
        project_description = get_description()
    except PyprojectTOMLError:
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
    (usethis_config.cpd() / "README.md").write_text(content, encoding="utf-8")
    how_print("Populate 'README.md' to help users understand the project.")
