"""Display project information."""

from __future__ import annotations

from typing import TYPE_CHECKING

from usethis._backend.dispatch import get_backend
from usethis._console import plain_print
from usethis._integrations.project.name import get_project_name
from usethis._integrations.sonarqube.config import get_sonar_project_properties

if TYPE_CHECKING:
    from pathlib import Path


def show_backend(*, output_file: Path | None = None) -> None:
    """Display the current package manager backend."""
    _output(get_backend().value, output_file=output_file)


def show_name(*, output_file: Path | None = None) -> None:
    """Display the project name."""
    _output(get_project_name(), output_file=output_file)


def show_sonarqube_config(
    *, project_key: str | None = None, output_file: Path | None = None
) -> None:
    """Display the SonarQube project configuration."""
    _output(
        get_sonar_project_properties(project_key=project_key), output_file=output_file
    )


def _output(content: str, *, output_file: Path | None = None) -> None:
    if output_file is not None:
        if not content.endswith("\n"):
            content += "\n"
        output_file.write_text(content, encoding="utf-8")
    else:
        plain_print(content)
