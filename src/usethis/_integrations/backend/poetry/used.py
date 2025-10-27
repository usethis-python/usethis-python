from usethis._config import usethis_config
from usethis._integrations.file.pyproject_toml.io_ import PyprojectTOMLManager


def is_poetry_used() -> bool:
    pyproject_toml_manager = PyprojectTOMLManager()

    return (
        (usethis_config.cpd() / "poetry.lock").exists()
        or (usethis_config.cpd() / "poetry.toml").exists()
        or (
            pyproject_toml_manager.path.exists()
            and ["tool", "poetry"] in pyproject_toml_manager
        )
    )
