import sys

from usethis._console import err_print
from usethis._integrations.pyproject.name import get_name
from usethis._integrations.sonarqube.config import get_sonar_project_properties
from usethis._integrations.uv.init import ensure_pyproject_toml
from usethis.errors import UsethisError


def show_name() -> None:
    ensure_pyproject_toml()
    print(get_name())


def show_sonarqube_config() -> None:
    ensure_pyproject_toml()
    try:
        print(get_sonar_project_properties())
    except UsethisError as err:
        err_print(err)
        sys.exit(1)
