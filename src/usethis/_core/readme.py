from pathlib import Path

from usethis._console import box_print, tick_print
from usethis._integrations.pyproject_toml.errors import PyprojectTOMLError
from usethis._integrations.pyproject_toml.name import get_description, get_name
from usethis._integrations.uv.init import ensure_pyproject_toml


def add_readme() -> None:
    """Add a README.md file to the project."""
    # Any file extension is fine, but we'll use '.md' for consistency.

    try:
        get_readme_path()
    except FileNotFoundError:
        pass
    else:
        return

    ensure_pyproject_toml()

    try:
        project_name = get_name()
    except PyprojectTOMLError:
        project_name = None

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
    (Path.cwd() / "README.md").write_text(content, encoding="utf-8")
    box_print("Populate 'README.md' to help users understand the project.")


def get_readme_path():
    path_readme_md = Path.cwd() / "README.md"
    path_readme = Path.cwd() / "README"

    if path_readme_md.exists() and path_readme_md.is_file():
        return path_readme_md
    elif path_readme.exists() and path_readme.is_file():
        return path_readme

    for path in Path.cwd().glob("README*"):
        if path.is_file() and path.stem == "README":
            return path

    msg = "No README file found."
    raise FileNotFoundError(msg)
