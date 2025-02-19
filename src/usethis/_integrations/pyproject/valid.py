from pathlib import Path

from tomlkit import TOMLDocument
from tomlkit.container import Container
from tomlkit.items import Table

from usethis._console import tick_print
from usethis._integrations.pyproject.io_ import (
    read_pyproject_toml,
    write_pyproject_toml,
)


def ensure_pyproject_validity():
    if not (Path.cwd() / "pyproject.toml").exists():
        return

    toml_document = read_pyproject_toml()

    project = _ensure_project_section(toml_document)
    _ensure_project_version(project)
    _ensure_project_name(project)

    write_pyproject_toml(toml_document)


def _ensure_project_section(toml_document: TOMLDocument) -> Table:
    if "project" not in toml_document:
        tick_print("Adding 'project' section to 'pyproject.toml'.")
        toml_document["project"] = {}

    project = toml_document["project"]
    if not isinstance(project, Table):
        msg = f"Expected 'project' to be a TOML Table, got {type(project)}."
        raise TypeError(msg)

    return project


def _ensure_project_version(project: Table) -> None:
    if "version" in project:
        return
    if "dynamic" in project:
        dynamic = project["dynamic"]
        if not isinstance(dynamic, Container):
            # Don't try to fix it if it's invalid
            return
        if "version" in dynamic:
            return
    tick_print("Setting project version to '0.1.0' in 'pyproject.toml'.")
    project["version"] = "0.1.0"


def _ensure_project_name(project: Table) -> None:
    if "name" in project:
        return

    # Use the name of the parent directory
    # Names must start and end with a letter or digit and may only contain -, _, ., and
    # alphanumeric characters. Any other characters will be dropped. If there are no
    # valid characters, the name will be "my_project".

    dir_name = Path.cwd().name
    name = "".join(c for c in dir_name if c.isalnum() or c in {"-", "_", "."})
    if not name:
        name = "my_project"

    tick_print(f"Setting project name to '{name}' in 'pyproject.toml'.")
    project["name"] = name
