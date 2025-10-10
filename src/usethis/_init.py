import re

from typing_extensions import assert_never

from usethis._config import usethis_config
from usethis._console import tick_print
from usethis._integrations.backend.dispatch import get_backend
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
        # pyproject.toml
        with usethis_config.set(alert_only=True):
            ensure_pyproject_toml()

        # README.md
        (usethis_config.cpd() / "README.md").touch(exist_ok=True)

        # src/
        src_dir = usethis_config.cpd() / "src"
        src_dir.mkdir(exist_ok=True)
        project_name = get_project_name()
        pkg_name = _regularize_package_name(project_name)
        (src_dir / pkg_name).mkdir(exist_ok=True)
        init_path = src_dir / pkg_name / "__init__.py"
        if not init_path.exists():
            init_path.write_text(
                f"""\
def hello() -> str:
    return "Hello from {project_name}!"
"""
            )
        (src_dir / pkg_name / "py.typed").touch(exist_ok=True)
    else:
        assert_never(backend)


def _regularize_package_name(project_name: str) -> str:
    """Regularize the package name to be suitable for Python packaging."""
    # https://peps.python.org/pep-0008/#package-and-module-names
    # Replace non-alphanumeric characters with underscores
    # Conjoin consecutive underscores
    # Add leading underscore if it starts with a digit

    project_name = re.sub(r"\W+", "_", project_name)
    project_name = re.sub(r"_+", "_", project_name)
    if project_name[0].isdigit():
        project_name = "_" + project_name
    return project_name.lower()


def ensure_dep_declaration_file() -> None:
    """Ensure that the file where dependencies are declared exists, if necessary."""
    backend = get_backend()
    if backend is BackendEnum.uv:
        ensure_pyproject_toml()
    elif backend is BackendEnum.none:
        # No dependencies are interacted with; we just display messages.
        pass
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
