import sys
from pathlib import Path

import pytest

from _test import change_cwd, is_uv_python_available, uv_python_pin
from usethis._config_file import files_manager
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._init import ensure_pyproject_toml
from usethis._integrations.sonarqube.config import (
    _validate_project_key,
    get_sonar_project_properties,
)
from usethis._integrations.sonarqube.errors import (
    CoverageReportConfigNotFoundError,
    InvalidSonarQubeProjectKeyError,
    MissingProjectKeyError,
)
from usethis._python.version import PythonVersion


class TestGetSonarProjectProperties:
    def test_dump_file(self, tmp_path: Path):
        # If the file already exists, we just return it.

        # Arrange
        path = tmp_path / "sonar-project.properties"
        contents = "foo=bar\n"
        path.write_text(contents)

        # Act
        with change_cwd(tmp_path):
            result = get_sonar_project_properties()

        # Assert
        assert result == contents

    @pytest.mark.skipif(
        not is_uv_python_available("3.13") or sys.version_info > (3, 13),
        reason="Requires Python 3.13 in uv and current Python <= 3.13 (otherwise requires-python blocks the pin)",
    )
    def test_file_doesnt_exist(self, uv_init_dir: Path):
        # If the file does not exist, we should construct based on information in
        # the repo.

        # Arrange
        with change_cwd(uv_init_dir), files_manager():
            PyprojectTOMLManager().set_value(
                keys=["tool", "usethis", "sonarqube", "project-key"], value="foobar"
            )
            PyprojectTOMLManager().set_value(
                keys=["tool", "coverage", "xml", "output"], value="coverage.xml"
            )
            uv_python_pin("3.13")
        content = (uv_init_dir / "pyproject.toml").read_text()
        assert "xml" in content

        # Act
        with change_cwd(uv_init_dir), files_manager():
            result = get_sonar_project_properties()

        # Assert
        assert (
            result
            == """\
sonar.projectKey=foobar
sonar.language=py
sonar.python.version=3.13
sonar.sources=./src
sonar.tests=./tests
sonar.python.coverage.reportPaths=coverage.xml
sonar.verbose=false
"""
        )

    def test_different_python_version(self, tmp_path: Path):
        # If the python version is different, it should be updated.

        with change_cwd(tmp_path), files_manager():
            # Arrange
            assert str(PythonVersion.from_interpreter())
            uv_python_pin("3.10")
            ensure_pyproject_toml()
            PyprojectTOMLManager().set_value(
                keys=["tool", "usethis", "sonarqube", "project-key"], value="foobar"
            )
            PyprojectTOMLManager().set_value(
                keys=["tool", "coverage", "xml", "output"], value="coverage.xml"
            )
        content = (tmp_path / "pyproject.toml").read_text()
        assert "xml" in content

        with change_cwd(tmp_path), files_manager():
            # Act
            result = get_sonar_project_properties()

        # Assert
        assert (
            result
            == """\
sonar.projectKey=foobar
sonar.language=py
sonar.python.version=3.10
sonar.sources=./
sonar.tests=./tests
sonar.python.coverage.reportPaths=coverage.xml
sonar.verbose=false
sonar.exclusions=tests/*
"""
        )

    def test_no_pin_python(self, tmp_path: Path):
        with change_cwd(tmp_path), files_manager():
            # Arrange
            ensure_pyproject_toml()
            PyprojectTOMLManager().set_value(
                keys=["tool", "usethis", "sonarqube", "project-key"], value="foobar"
            )
            PyprojectTOMLManager().set_value(
                keys=["tool", "coverage", "xml", "output"], value="coverage.xml"
            )

            # Act
            result = get_sonar_project_properties()

        # Assert
        assert (
            result
            == f"""\
sonar.projectKey=foobar
sonar.language=py
sonar.python.version={PythonVersion.from_interpreter()!s}
sonar.sources=./
sonar.tests=./tests
sonar.python.coverage.reportPaths=coverage.xml
sonar.verbose=false
sonar.exclusions=tests/*
"""
        )

    def test_different_project_key(self, tmp_path: Path):
        with change_cwd(tmp_path), files_manager():
            # Arrange
            uv_python_pin("3.12")
            ensure_pyproject_toml()
            PyprojectTOMLManager().set_value(
                keys=["tool", "usethis", "sonarqube", "project-key"], value="different"
            )
            PyprojectTOMLManager().set_value(
                keys=["tool", "coverage", "xml", "output"], value="coverage.xml"
            )

            # Act
            result = get_sonar_project_properties()

        # Assert
        assert (
            result
            == """\
sonar.projectKey=different
sonar.language=py
sonar.python.version=3.12
sonar.sources=./
sonar.tests=./tests
sonar.python.coverage.reportPaths=coverage.xml
sonar.verbose=false
sonar.exclusions=tests/*
"""
        )

    def test_set_verbose_true(self, tmp_path: Path):
        with change_cwd(tmp_path), files_manager():
            # Arrange
            uv_python_pin("3.12")
            ensure_pyproject_toml()
            PyprojectTOMLManager().set_value(
                keys=["tool", "usethis", "sonarqube", "project-key"], value="foobar"
            )
            PyprojectTOMLManager().set_value(
                keys=["tool", "usethis", "sonarqube", "verbose"], value=True
            )
            PyprojectTOMLManager().set_value(
                keys=["tool", "coverage", "xml", "output"], value="coverage.xml"
            )

            # Act
            result = get_sonar_project_properties()

        # Assert
        assert (
            result
            == """\
sonar.projectKey=foobar
sonar.language=py
sonar.python.version=3.12
sonar.sources=./
sonar.tests=./tests
sonar.python.coverage.reportPaths=coverage.xml
sonar.verbose=true
sonar.exclusions=tests/*
"""
        )

    def test_missing_pyproject_toml_raises(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.delenv("SONAR_PROJECT_KEY", raising=False)
        with (
            change_cwd(tmp_path),
            files_manager(),
            pytest.raises(MissingProjectKeyError),
        ):
            get_sonar_project_properties()

    def test_missing_project_key_section_raises(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.delenv("SONAR_PROJECT_KEY", raising=False)
        with change_cwd(tmp_path), files_manager():
            # Arrange
            ensure_pyproject_toml()

            # Act, Assert
            with pytest.raises(MissingProjectKeyError):
                get_sonar_project_properties()

    def test_non_string_project_key_raises(self, tmp_path: Path):
        with change_cwd(tmp_path), files_manager():
            # Arrange
            ensure_pyproject_toml()
            PyprojectTOMLManager().set_value(
                keys=["tool", "usethis", "sonarqube", "project-key"], value=123
            )

            # Act, Assert
            with pytest.raises(MissingProjectKeyError):
                get_sonar_project_properties()

    def test_patch_version_ignored(self, tmp_path: Path):
        with change_cwd(tmp_path), files_manager():
            # Arrange
            uv_python_pin("3.12.1")
            ensure_pyproject_toml()
            PyprojectTOMLManager().set_value(
                keys=["tool", "usethis", "sonarqube", "project-key"], value="foobar"
            )
            PyprojectTOMLManager().set_value(
                keys=["tool", "coverage", "xml", "output"], value="coverage.xml"
            )

            # Act
            result = get_sonar_project_properties()

        # Assert
        assert (
            result
            == """\
sonar.projectKey=foobar
sonar.language=py
sonar.python.version=3.12
sonar.sources=./
sonar.tests=./tests
sonar.python.coverage.reportPaths=coverage.xml
sonar.verbose=false
sonar.exclusions=tests/*
"""
        )

    def test_exclusions(self, tmp_path: Path):
        with change_cwd(tmp_path), files_manager():
            # Arrange
            uv_python_pin("3.12")
            ensure_pyproject_toml()
            PyprojectTOMLManager().set_value(
                keys=["tool", "usethis", "sonarqube", "project-key"], value="foobar"
            )
            PyprojectTOMLManager().set_value(
                keys=["tool", "usethis", "sonarqube", "exclusions"],
                value=[
                    "**/Dockerfile",
                    "src/notebooks/**/*",
                ],
            )
            PyprojectTOMLManager().set_value(
                keys=["tool", "coverage", "xml", "output"], value="coverage.xml"
            )

            # Act
            result = get_sonar_project_properties()

        # Assert
        assert (
            result
            == """\
sonar.projectKey=foobar
sonar.language=py
sonar.python.version=3.12
sonar.sources=./
sonar.tests=./tests
sonar.python.coverage.reportPaths=coverage.xml
sonar.verbose=false
sonar.exclusions=tests/*, **/Dockerfile, src/notebooks/**/*
"""
        )

    def test_different_coverage_file_location(self, tmp_path: Path):
        with change_cwd(tmp_path), files_manager():
            # Arrange
            uv_python_pin("3.12")
            ensure_pyproject_toml()
            PyprojectTOMLManager().set_value(
                keys=["tool", "usethis", "sonarqube", "project-key"], value="foobar"
            )
            PyprojectTOMLManager().set_value(
                keys=["tool", "coverage", "xml", "output"],
                value="./test-reports/cov.xml",
            )

            # Act
            result = get_sonar_project_properties()

        # Assert
        assert (
            result
            == """\
sonar.projectKey=foobar
sonar.language=py
sonar.python.version=3.12
sonar.sources=./
sonar.tests=./tests
sonar.python.coverage.reportPaths=./test-reports/cov.xml
sonar.verbose=false
sonar.exclusions=tests/*
"""
        )

    def test_missing_coverage_file_location_error(self, tmp_path: Path):
        with change_cwd(tmp_path), files_manager():
            # Arrange
            uv_python_pin("3.12")
            ensure_pyproject_toml()
            PyprojectTOMLManager().set_value(
                keys=["tool", "usethis", "sonarqube", "project-key"], value="foobar"
            )

            # Act, Assert
            with pytest.raises(CoverageReportConfigNotFoundError):
                get_sonar_project_properties()

    def test_project_key_argument(self, tmp_path: Path):
        with change_cwd(tmp_path), files_manager():
            # Arrange
            uv_python_pin("3.12")
            ensure_pyproject_toml()
            PyprojectTOMLManager().set_value(
                keys=["tool", "coverage", "xml", "output"], value="coverage.xml"
            )

            # Act
            result = get_sonar_project_properties(project_key="cli-key")

        # Assert
        assert (
            result
            == """\
sonar.projectKey=cli-key
sonar.language=py
sonar.python.version=3.12
sonar.sources=./
sonar.tests=./tests
sonar.python.coverage.reportPaths=coverage.xml
sonar.verbose=false
sonar.exclusions=tests/*
"""
        )

    def test_project_key_argument_overrides_pyproject(self, tmp_path: Path):
        with change_cwd(tmp_path), files_manager():
            # Arrange
            uv_python_pin("3.12")
            ensure_pyproject_toml()
            PyprojectTOMLManager().set_value(
                keys=["tool", "usethis", "sonarqube", "project-key"],
                value="from-pyproject",
            )
            PyprojectTOMLManager().set_value(
                keys=["tool", "coverage", "xml", "output"], value="coverage.xml"
            )

            # Act
            result = get_sonar_project_properties(project_key="from-cli")

        # Assert
        assert "sonar.projectKey=from-cli\n" in result

    def test_project_key_argument_invalid(self, tmp_path: Path):
        with change_cwd(tmp_path), files_manager():
            # Arrange
            uv_python_pin("3.12")
            ensure_pyproject_toml()
            PyprojectTOMLManager().set_value(
                keys=["tool", "coverage", "xml", "output"], value="coverage.xml"
            )

            # Act, Assert
            with pytest.raises(InvalidSonarQubeProjectKeyError):
                get_sonar_project_properties(project_key="invalid key!")

    def test_flat_layout_exclusions_already_has_tests(self, tmp_path: Path):
        # When using flat layout and tests/* is already in exclusions,
        # it should not be added again.

        with change_cwd(tmp_path), files_manager():
            # Arrange
            uv_python_pin("3.12")
            ensure_pyproject_toml()
            PyprojectTOMLManager().set_value(
                keys=["tool", "usethis", "sonarqube", "project-key"], value="foobar"
            )
            PyprojectTOMLManager().set_value(
                keys=["tool", "usethis", "sonarqube", "exclusions"],
                value=["tests/*", "**/Dockerfile"],
            )
            PyprojectTOMLManager().set_value(
                keys=["tool", "coverage", "xml", "output"], value="coverage.xml"
            )

            # Act
            result = get_sonar_project_properties()

        # Assert
        assert (
            result
            == """\
sonar.projectKey=foobar
sonar.language=py
sonar.python.version=3.12
sonar.sources=./
sonar.tests=./tests
sonar.python.coverage.reportPaths=coverage.xml
sonar.verbose=false
sonar.exclusions=tests/*, **/Dockerfile
"""
        )

    def test_env_var_project_key(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        # SONAR_PROJECT_KEY env var is used when no CLI arg and no pyproject.toml config.

        monkeypatch.setenv("SONAR_PROJECT_KEY", "from-env")

        with change_cwd(tmp_path), files_manager():
            # Arrange
            uv_python_pin("3.12")
            ensure_pyproject_toml()
            PyprojectTOMLManager().set_value(
                keys=["tool", "coverage", "xml", "output"], value="coverage.xml"
            )

            # Act
            result = get_sonar_project_properties()

        # Assert
        assert "sonar.projectKey=from-env\n" in result

    def test_env_var_overrides_pyproject(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        # SONAR_PROJECT_KEY env var takes priority over pyproject.toml config.

        monkeypatch.setenv("SONAR_PROJECT_KEY", "from-env")

        with change_cwd(tmp_path), files_manager():
            # Arrange
            uv_python_pin("3.12")
            ensure_pyproject_toml()
            PyprojectTOMLManager().set_value(
                keys=["tool", "usethis", "sonarqube", "project-key"],
                value="from-pyproject",
            )
            PyprojectTOMLManager().set_value(
                keys=["tool", "coverage", "xml", "output"], value="coverage.xml"
            )

            # Act
            result = get_sonar_project_properties()

        # Assert
        assert "sonar.projectKey=from-env\n" in result

    def test_cli_arg_overrides_env_var(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        # CLI --project-key takes priority over SONAR_PROJECT_KEY env var.

        monkeypatch.setenv("SONAR_PROJECT_KEY", "from-env")

        with change_cwd(tmp_path), files_manager():
            # Arrange
            uv_python_pin("3.12")
            ensure_pyproject_toml()
            PyprojectTOMLManager().set_value(
                keys=["tool", "coverage", "xml", "output"], value="coverage.xml"
            )

            # Act
            result = get_sonar_project_properties(project_key="from-cli")

        # Assert
        assert "sonar.projectKey=from-cli\n" in result

    def test_env_var_invalid_raises(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        # An invalid SONAR_PROJECT_KEY env var raises InvalidSonarQubeProjectKeyError.

        monkeypatch.setenv("SONAR_PROJECT_KEY", "invalid key!")

        with change_cwd(tmp_path), files_manager():
            # Arrange
            uv_python_pin("3.12")
            ensure_pyproject_toml()
            PyprojectTOMLManager().set_value(
                keys=["tool", "coverage", "xml", "output"], value="coverage.xml"
            )

            # Act, Assert
            with pytest.raises(InvalidSonarQubeProjectKeyError):
                get_sonar_project_properties()

    def test_env_var_no_pyproject_coverage_raises(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        # When SONAR_PROJECT_KEY is set but pyproject.toml is missing entirely,
        # CoverageReportConfigNotFoundError is raised (coverage output lookup fails).

        monkeypatch.setenv("SONAR_PROJECT_KEY", "from-env")

        with (
            change_cwd(tmp_path),
            files_manager(),
            pytest.raises(CoverageReportConfigNotFoundError),
        ):
            get_sonar_project_properties()


class TestValidateProjectKey:
    def test_valid(self):
        # Arrange
        project_key = "foo:bar"

        # Act
        result = _validate_project_key(project_key)

        # Assert
        assert result is None

    def test_bad_characters(self):
        # Arrange
        project_key = "foo bar"

        # Act, Assert
        with pytest.raises(InvalidSonarQubeProjectKeyError):
            _validate_project_key(project_key)

    def test_missing_non_digit(self):
        # The key must contain at least one non-digit character.

        # Arrange
        project_key = "123"

        # Act, Assert
        with pytest.raises(InvalidSonarQubeProjectKeyError):
            _validate_project_key(project_key)
