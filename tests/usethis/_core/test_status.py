from pathlib import Path

import pytest
from pydantic import TypeAdapter  # noqa: TID251

from _test import change_cwd
from usethis._config_file import files_manager
from usethis._core.status import _STATUS_TO_CLASSIFIER_MAP, use_development_status
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._types.status import DevelopmentStatusEnum


class TestStatusToClassifierMap:
    def test_keys_match_enum(self):
        assert set(_STATUS_TO_CLASSIFIER_MAP.keys()) == set(DevelopmentStatusEnum)


class TestUseDevelopmentStatus:
    def test_planning(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
        # Arrange
        status = DevelopmentStatusEnum.planning

        # Act
        with change_cwd(uv_init_dir), files_manager():
            use_development_status(status)

        # Assert
        assert (
            "Development Status :: 1 - Planning"
            in uv_init_dir.joinpath("pyproject.toml").read_text()
        )
        with files_manager():
            mgr = PyprojectTOMLManager()
            assert "Development Status :: 1 - Planning" in TypeAdapter(
                list[str]
            ).validate_python(mgr[["project", "classifiers"]])
        out, err = capfd.readouterr()
        assert not err
        assert out == "✔ Setting the development status to '1 - Planning'.\n"

    def test_planning_code(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
        # Arrange
        status = DevelopmentStatusEnum.planning_code

        # Act
        with change_cwd(uv_init_dir), files_manager():
            use_development_status(status)

        # Assert
        assert (
            "Development Status :: 1 - Planning"
            in uv_init_dir.joinpath("pyproject.toml").read_text()
        )
        with files_manager():
            mgr = PyprojectTOMLManager()
            assert "Development Status :: 1 - Planning" in TypeAdapter(
                list[str]
            ).validate_python(mgr[["project", "classifiers"]])
        out, err = capfd.readouterr()
        assert not err
        assert out == "✔ Setting the development status to '1 - Planning'.\n"

    def test_prealpha(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
        # Arrange
        status = DevelopmentStatusEnum.prealpha

        # Act
        with change_cwd(uv_init_dir), files_manager():
            use_development_status(status)

        # Assert
        assert (
            "Development Status :: 2 - Pre-Alpha"
            in uv_init_dir.joinpath("pyproject.toml").read_text()
        )
        with files_manager():
            mgr = PyprojectTOMLManager()
            assert "Development Status :: 2 - Pre-Alpha" in TypeAdapter(
                list[str]
            ).validate_python(mgr[["project", "classifiers"]])
        out, err = capfd.readouterr()
        assert not err
        assert out == "✔ Setting the development status to '2 - Pre-Alpha'.\n"

    def test_alpha(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
        # Arrange
        status = DevelopmentStatusEnum.alpha

        # Act
        with change_cwd(uv_init_dir), files_manager():
            use_development_status(status)

        # Assert
        assert (
            "Development Status :: 3 - Alpha"
            in uv_init_dir.joinpath("pyproject.toml").read_text()
        )
        with files_manager():
            mgr = PyprojectTOMLManager()
            assert "Development Status :: 3 - Alpha" in TypeAdapter(
                list[str]
            ).validate_python(mgr[["project", "classifiers"]])
        out, err = capfd.readouterr()
        assert not err
        assert out == "✔ Setting the development status to '3 - Alpha'.\n"

    def test_beta(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
        # Arrange
        status = DevelopmentStatusEnum.beta

        # Act
        with change_cwd(uv_init_dir), files_manager():
            use_development_status(status)

        # Assert
        assert (
            "Development Status :: 4 - Beta"
            in uv_init_dir.joinpath("pyproject.toml").read_text()
        )
        with files_manager():
            mgr = PyprojectTOMLManager()
            assert "Development Status :: 4 - Beta" in TypeAdapter(
                list[str]
            ).validate_python(mgr[["project", "classifiers"]])
        out, err = capfd.readouterr()
        assert not err
        assert out == "✔ Setting the development status to '4 - Beta'.\n"

    def test_production(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
        # Arrange
        status = DevelopmentStatusEnum.production

        # Act
        with change_cwd(uv_init_dir), files_manager():
            use_development_status(status)

        # Assert
        assert (
            "Development Status :: 5 - Production/Stable"
            in uv_init_dir.joinpath("pyproject.toml").read_text()
        )
        with files_manager():
            mgr = PyprojectTOMLManager()
            assert "Development Status :: 5 - Production/Stable" in TypeAdapter(
                list[str]
            ).validate_python(mgr[["project", "classifiers"]])
        out, err = capfd.readouterr()
        assert not err
        assert out == "✔ Setting the development status to '5 - Production/Stable'.\n"

    def test_mature(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
        # Arrange
        status = DevelopmentStatusEnum.mature

        # Act
        with change_cwd(uv_init_dir), files_manager():
            use_development_status(status)

        # Assert
        assert (
            "Development Status :: 6 - Mature"
            in uv_init_dir.joinpath("pyproject.toml").read_text()
        )
        with files_manager():
            mgr = PyprojectTOMLManager()
            assert "Development Status :: 6 - Mature" in TypeAdapter(
                list[str]
            ).validate_python(mgr[["project", "classifiers"]])
        out, err = capfd.readouterr()
        assert not err
        assert out == "✔ Setting the development status to '6 - Mature'.\n"

    def test_inactive(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
        # Arrange
        status = DevelopmentStatusEnum.inactive

        # Act
        with change_cwd(uv_init_dir), files_manager():
            use_development_status(status)

        # Assert
        assert (
            "Development Status :: 7 - Inactive"
            in uv_init_dir.joinpath("pyproject.toml").read_text()
        )
        with files_manager():
            mgr = PyprojectTOMLManager()
            assert "Development Status :: 7 - Inactive" in TypeAdapter(
                list[str]
            ).validate_python(mgr[["project", "classifiers"]])
        out, err = capfd.readouterr()
        assert not err
        assert out == "✔ Setting the development status to '7 - Inactive'.\n"

    def test_no_pyproject_toml(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
        # Arrange
        status = DevelopmentStatusEnum.planning

        # Act
        with change_cwd(tmp_path), files_manager():
            use_development_status(status)

        # Assert
        out, err = capfd.readouterr()
        assert not err
        assert out == (
            "✔ Writing 'pyproject.toml'.\n"
            "✔ Setting the development status to '1 - Planning'.\n"
        )

    def test_replace_existing_classifier(
        self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]
    ):
        # Arrange
        status = DevelopmentStatusEnum.beta

        # Create an existing classifier
        (uv_init_dir / "pyproject.toml").write_text(
            """\
[project]
classifiers = [
    "Development Status :: 3 - Alpha",
]
"""
        )

        # Act
        with change_cwd(uv_init_dir), files_manager():
            use_development_status(status)

        # Assert
        assert (
            "Development Status :: 4 - Beta"
            in uv_init_dir.joinpath("pyproject.toml").read_text()
        )
        with files_manager():
            mgr = PyprojectTOMLManager()
            assert mgr[["project", "classifiers"]] == ["Development Status :: 4 - Beta"]
            assert "Development Status :: 3 - Alpha" not in TypeAdapter(
                list[str]
            ).validate_python(mgr[["project", "classifiers"]])
        out, err = capfd.readouterr()
        assert not err
        assert out == "✔ Setting the development status to '4 - Beta'.\n"

    def test_replace_multiple_existing_classifiers(
        self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]
    ):
        # Arrange
        status = DevelopmentStatusEnum.production

        # Create existing classifiers
        (uv_init_dir / "pyproject.toml").write_text(
            """\
[project]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Development Status :: 4 - Beta",
]
"""
        )

        # Act
        with change_cwd(uv_init_dir), files_manager():
            use_development_status(status)

        # Assert
        assert (
            "Development Status :: 5 - Production/Stable"
            in uv_init_dir.joinpath("pyproject.toml").read_text()
        )
        with files_manager():
            mgr = PyprojectTOMLManager()
            assert mgr[["project", "classifiers"]] == [
                "Development Status :: 5 - Production/Stable"
            ]
            assert "Development Status :: 3 - Alpha" not in TypeAdapter(
                list[str]
            ).validate_python(mgr[["project", "classifiers"]])
            assert "Development Status :: 4 - Beta" not in TypeAdapter(
                list[str]
            ).validate_python(mgr[["project", "classifiers"]])
        out, err = capfd.readouterr()
        assert not err
        assert out == "✔ Setting the development status to '5 - Production/Stable'.\n"
