from __future__ import annotations

from usethis._config import usethis_config
from usethis._integrations.file.pyproject_toml.name import get_name
from usethis._integrations.sonarqube.config import get_sonar_project_properties
from usethis._integrations.uv.init import ensure_pyproject_toml


def show_name() -> None:
    with usethis_config.set(quiet=True):
        ensure_pyproject_toml()
    print(get_name())


def show_sonarqube_config() -> None:
    with usethis_config.set(quiet=True):
        ensure_pyproject_toml()
    get_sonar_project_properties()
