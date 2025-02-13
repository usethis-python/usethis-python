from collections.abc import Container
from pathlib import Path

from usethis._console import tick_print
from usethis._integrations.pyproject.io_ import (
    read_pyproject_toml,
    write_pyproject_toml,
)


def ensure_pyproject_validity():
    if not (Path.cwd() / "pyproject.toml").exists():
        return

    toml_document = read_pyproject_toml()

    # If project.version is missing and project.dynamic does not include "version",
    # then we should add the version as 0.1.0 automatically.
    if "project" not in toml_document:
        toml_document["project"] = {}
    project = toml_document["project"]
    if not isinstance(project, Container):
        # Don't try to fix it if it's invalid
        return
    if "version" in project:
        return
    if "dynamic" in project:
        dynamic = project["dynamic"]
        if not isinstance(dynamic, Container):
            # Again, don't try to fix it if it's invalid
            return
        if "version" in dynamic:
            return
    # We're here so we should add the version
    project["version"] = "0.1.0"
    tick_print("Set project version to '0.1.0' in 'pyproject.toml'.")

    write_pyproject_toml(toml_document)
