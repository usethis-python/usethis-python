"""Detection of Poetry usage in a project."""

from usethis._backend.poetry.available import is_poetry_available
from usethis._config import usethis_config
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager


def is_poetry_used() -> bool:
    """Check if Poetry is being used in the project."""
    pyproject_toml_manager = PyprojectTOMLManager()

    return (
        (usethis_config.cpd() / "poetry.lock").exists()
        or (usethis_config.cpd() / "poetry.toml").exists()
        or (
            pyproject_toml_manager.path.exists()
            and ["tool", "poetry"] in pyproject_toml_manager
        )
        or is_poetry_available()
    )
