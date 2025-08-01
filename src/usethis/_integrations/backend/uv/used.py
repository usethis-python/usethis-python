from usethis._config import usethis_config
from usethis._integrations.file.pyproject_toml.io_ import PyprojectTOMLManager


def is_uv_used() -> bool:
    pyproject_toml_manager = PyprojectTOMLManager()

    return (
        (usethis_config.cpd() / "uv.lock").exists()
        or (usethis_config.cpd() / "uv.toml").exists()
        or (
            pyproject_toml_manager.path.exists()
            and ["tool", "uv"] in pyproject_toml_manager
        )
    )
