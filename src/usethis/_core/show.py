from __future__ import annotations

from usethis._console import plain_print
from usethis._integrations.backend.dispatch import get_backend
from usethis._integrations.project.name import get_project_name
from usethis._integrations.sonarqube.config import get_sonar_project_properties


def show_backend() -> None:
    plain_print(get_backend().value)


def show_name() -> None:
    plain_print(get_project_name())


def show_sonarqube_config() -> None:
    plain_print(get_sonar_project_properties())
