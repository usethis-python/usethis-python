from typing_extensions import assert_never

from usethis._backend import get_backend
from usethis._config import usethis_config
from usethis._console import tick_print
from usethis._integrations.backend.uv.init import (
    ensure_pyproject_toml_via_uv,
    opinionated_uv_init,
)
from usethis._integrations.file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._integrations.project.name import get_project_name
from usethis._types.backend import BackendEnum


def project_init():
    if (usethis_config.cpd() / "pyproject.toml").exists():
        return

    tick_print("Writing 'pyproject.toml' and initializing project.")

    backend = get_backend()
    if backend is BackendEnum.uv:
        opinionated_uv_init()
    elif backend is BackendEnum.none:
        raise NotImplementedError
    else:
        assert_never(backend)


def ensure_pyproject_toml(*, author: bool = True) -> None:
    if (usethis_config.cpd() / "pyproject.toml").exists():
        return

    tick_print("Writing 'pyproject.toml'.")
    backend = get_backend()
    if backend is BackendEnum.uv:
        ensure_pyproject_toml_via_uv(author=author)
    elif backend is BackendEnum.none:
        (usethis_config.cpd() / "pyproject.toml").write_text(
            f"""\
[project]
name = "{get_project_name()}"
version = "0.1.0"
dependencies = []

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
"""
        )
    else:
        assert_never(backend)

    if not (
        (usethis_config.cpd() / "src").exists()
        and (usethis_config.cpd() / "src").is_dir()
    ):
        # hatch needs to know where to find the package
        PyprojectTOMLManager().set_value(
            keys=["tool", "hatch", "build", "targets", "wheel", "packages"],
            value=["."],
        )
