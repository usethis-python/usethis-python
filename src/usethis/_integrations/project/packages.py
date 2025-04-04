import pkgutil
from pathlib import Path

from typing_extensions import assert_never

from usethis._integrations.project.layout import get_source_dir_str

IMPORTABLE_PACKAGE_EXCLUSIONS = {"tests", "test", "doc", "docs"}


def get_importable_packages() -> list[str]:
    """Get the names of packages in the source directory that can be imported.

    These are not necessarily the import packages distributed with the project, since
    that depends on build tool configuration. We are mostly interested in directories
    eligible for import analysis with tools like import-linter.
    """
    source_dir_str = get_source_dir_str()

    if source_dir_str in ("src", "."):
        path = Path.cwd() / source_dir_str
    else:
        assert_never(source_dir_str)

    packages = _get_packages_in_dir(path)

    if packages:
        return packages

    # Otherwise, perhaps it's a namespace package. We will only search one level deep
    # though.
    for parent in path.iterdir():
        if parent.is_dir() and not _is_excluded(parent.name):
            # Check if the directory is a package by looking for an __init__.py file
            packages.extend(
                [
                    f"{parent.name}.{module_name}"
                    for _, module_name, _ in pkgutil.iter_modules([parent])
                    if not _is_excluded(module_name)
                ]
            )

    return packages


def _get_packages_in_dir(path: Path) -> list[str]:
    """Get the names of packages in the given directory."""
    return [
        module_name
        for _, module_name, _ in pkgutil.iter_modules([path])
        if not _is_excluded(module_name)
    ]


def _is_excluded(name: str) -> bool:
    """Check if the given name is excluded from importable packages."""
    return name.strip("_.") in IMPORTABLE_PACKAGE_EXCLUSIONS
