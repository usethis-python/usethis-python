from __future__ import annotations

import re

from pydantic import TypeAdapter

from usethis._config import usethis_config
from usethis._integrations.file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._integrations.project.layout import get_source_dir_str
from usethis._integrations.python.version import get_python_version
from usethis._integrations.sonarqube.errors import (
    CoverageReportConfigNotFoundError,
    InvalidSonarQubeProjectKeyError,
    MissingProjectKeyError,
)


class _NonstandardPythonVersionError(Exception):
    """Raised when a non-standard Python version is detected."""


def get_sonar_project_properties() -> str:
    """Get contents for (or from) the sonar-project.properties file."""
    path = usethis_config.cpd() / "sonar-project.properties"
    if path.exists() and path.is_file():
        return path.read_text(encoding="utf-8")

    # Get Python version
    try:
        python_version = _get_short_version(
            (usethis_config.cpd() / ".python-version").read_text().strip()
        )
    except (FileNotFoundError, _NonstandardPythonVersionError):
        python_version = get_python_version()

    project_key = _get_sonarqube_project_key()
    verbose = _is_sonarqube_verbose()
    exclusions = _get_sonarqube_exclusions()

    # Get coverage report output path
    try:
        coverage_output = PyprojectTOMLManager()[["tool", "coverage", "xml", "output"]]
    except KeyError:
        msg = "XML coverage report file path not found at 'tool.coverage.xml.output' in 'pyproject.toml'."
        raise CoverageReportConfigNotFoundError(msg) from None
    except FileNotFoundError:
        msg = "Could not find 'pyproject.toml' for coverage report file path at 'tool.coverage.xml.output'."
        raise CoverageReportConfigNotFoundError(msg) from None

    # No file, so construct the contents
    source_dir_str = get_source_dir_str()
    if source_dir_str == ".":
        sources = "./"
        # When using flat layout, exclude tests directory to avoid double indexing
        if "tests/*" not in exclusions:
            exclusions.insert(0, "tests/*")
    else:
        sources = f"./{source_dir_str}"

    text = f"""\
sonar.projectKey={project_key}
sonar.language=py
sonar.python.version={python_version}
sonar.sources={sources}
sonar.tests=./tests
sonar.python.coverage.reportPaths={coverage_output}
sonar.verbose={"true" if verbose else "false"}
"""
    if exclusions:
        text += "sonar.exclusions=" + ", ".join(exclusions) + "\n"
    return text


def _get_short_version(version: str) -> str:
    match = re.match(r"^(\d{1,2}\.\d{1,2})", version)
    if match is None:
        msg = f"Could not parse Python version from '{version}'."
        raise _NonstandardPythonVersionError(msg)

    return match.group(1)


def _get_sonarqube_project_key() -> str:
    try:
        project_key = PyprojectTOMLManager()[
            ["tool", "usethis", "sonarqube", "project-key"]
        ]
    except KeyError:
        msg = "Could not find SonarQube project key at 'tool.usethis.sonarqube.project-key' in 'pyproject.toml'."
        raise MissingProjectKeyError(msg) from None
    except FileNotFoundError:
        msg = "Could not find 'pyproject.toml' for SonarQube project key at 'tool.usethis.sonarqube.project-key'."
        raise MissingProjectKeyError(msg) from None
    _validate_project_key(project_key)
    return project_key


def _is_sonarqube_verbose() -> bool:
    try:
        verbose = PyprojectTOMLManager()[["tool", "usethis", "sonarqube", "verbose"]]
    except (FileNotFoundError, KeyError):
        verbose = False
    verbose = TypeAdapter(bool).validate_python(verbose)

    return verbose


def _get_sonarqube_exclusions() -> list[str]:
    try:
        exclusions = PyprojectTOMLManager()[
            ["tool", "usethis", "sonarqube", "exclusions"]
        ]
    except (FileNotFoundError, KeyError):
        exclusions = []
    # TypeAdapter(list).validate_python() ensures we have a list and returns a new list
    exclusions = TypeAdapter(list).validate_python(exclusions)
    for exclusion in exclusions:
        TypeAdapter(str).validate_python(exclusion)

    return exclusions


def _validate_project_key(project_key: str) -> None:
    """Validate the SonarQube project key.

    The key must contain at least one non-digit character.
    Allowed characters are:
    a through z,
    A through Z,
    - (dash),
    _ (underscore),
    . (dot),
    : (colon)
    and the digits 0 through 9.

    This value is case-sensitive.
    """
    _RE = r"^[a-zA-Z0-9\-_:.]+$"
    if re.match(_RE, project_key) is None or project_key.isdigit():
        msg = f"Invalid SonarQube project key: '{project_key}'."
        raise InvalidSonarQubeProjectKeyError(msg)
