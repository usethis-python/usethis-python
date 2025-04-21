from usethis._integrations.file.pyproject_toml.io_ import PyprojectTOMLManager


def has_pyproject_toml_declared_build_system() -> bool:
    """Check if a build system is declared in the project."""
    return ["build-system"] in PyprojectTOMLManager()
