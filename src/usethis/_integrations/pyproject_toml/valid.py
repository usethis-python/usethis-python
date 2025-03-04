from pathlib import Path

from tomlkit import TOMLDocument
from tomlkit.items import Array, Table

from usethis._console import tick_print
from usethis._integrations.pyproject_toml.io_ import PyprojectTOMLManager


def ensure_pyproject_validity():
    if not (Path.cwd() / "pyproject.toml").exists():
        return

    toml_document = PyprojectTOMLManager().get()

    try:
        project = _ensure_project_section(toml_document)
        _ensure_project_name(project)
        _ensure_project_version(project)
    except TypeError:
        # Give up - the file is badly formatted. Let uv give a better error message.
        return

    PyprojectTOMLManager().commit(toml_document)


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
        if isinstance(dynamic, Array) and "version" in dynamic:
            # N.B. if the dynamic section is in the wrong format then
            # we will put 'version' in the project section.
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
    if project._value:
        project._value._insert_at(0, "name", name)
    else:
        project["name"] = name
