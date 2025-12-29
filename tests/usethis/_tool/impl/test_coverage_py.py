from pathlib import Path

from usethis._config_file import DotCoverageRCTOMLManager, files_manager
from usethis._integrations.file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._test import change_cwd
from usethis._tool.impl.coverage_py import CoveragePyTool


class TestCoveragePyTool:
    class TestAddConfigs:
        def test_after_codespell(self, tmp_path: Path):
            # To check the config is valid
            # https://github.com/usethis-python/usethis-python/issues/558

            # Arrange
            (tmp_path / "pyproject.toml").write_text("""\
[project]
name = "example"
version = "0.1.0"
description = "Add your description here"

[dependency-groups]
dev = [
    "codespell>=2.4.1",
]
                                                    
[tool.codespell]
ignore-regex = ["[A-Za-z0-9+/]{100,}"]
""")

            # Act
            with change_cwd(tmp_path), files_manager():
                CoveragePyTool().add_configs()

            # Assert
            with change_cwd(tmp_path), files_manager():
                assert ["tool", "coverage"] in PyprojectTOMLManager()
            assert "[tool.coverage]" in (tmp_path / "pyproject.toml").read_text()

    class TestAddConfig:
        def test_empty_dir(self, tmp_path: Path):
            # Expect .coveragerc to be preferred

            # Act
            with change_cwd(tmp_path), files_manager():
                CoveragePyTool().add_configs()

            # Assert
            assert (tmp_path / ".coveragerc").exists()
            assert not (tmp_path / "pyproject.toml").exists()

        def test_pyproject_toml_exists(self, tmp_path: Path):
            # Arrange
            (tmp_path / "pyproject.toml").touch()

            # Act
            with change_cwd(tmp_path), files_manager():
                CoveragePyTool().add_configs()

            # Assert
            assert not (tmp_path / ".coveragerc").exists()
            assert (tmp_path / "pyproject.toml").exists()

        def test_coveragerc_toml_exists(self, tmp_path: Path):
            # Arrange
            (tmp_path / ".coveragerc.toml").touch()

            # Act
            with change_cwd(tmp_path), files_manager():
                CoveragePyTool().add_configs()

            # Assert
            assert not (tmp_path / ".coveragerc").exists()
            assert (tmp_path / ".coveragerc.toml").exists()
            assert not (tmp_path / "pyproject.toml").exists()

        def test_coveragerc_toml_preferred_over_pyproject_toml(self, tmp_path: Path):
            # Arrange - both files exist, .coveragerc.toml should be used
            (tmp_path / "pyproject.toml").touch()
            (tmp_path / ".coveragerc.toml").touch()

            # Act
            with change_cwd(tmp_path), files_manager():
                CoveragePyTool().add_configs()

            # Assert - config should be added to .coveragerc.toml
            with change_cwd(tmp_path), files_manager():
                assert ["run"] in DotCoverageRCTOMLManager()
            content = (tmp_path / ".coveragerc.toml").read_text()
            assert "[run]" in content
            assert "[report]" in content
            assert (tmp_path / "pyproject.toml").read_text() == ""

        def test_coveragerc_preferred_over_coveragerc_toml(self, tmp_path: Path):
            # Arrange - both .coveragerc and .coveragerc.toml exist
            (tmp_path / ".coveragerc").write_text("[run]\nsource = existing\n")
            (tmp_path / ".coveragerc.toml").write_text('[run]\nsource = ["existing"]\n')

            # Act
            with change_cwd(tmp_path), files_manager():
                CoveragePyTool().add_configs()

            # Assert - .coveragerc should take priority
            coveragerc_content = (tmp_path / ".coveragerc").read_text()
            assert "[run]" in coveragerc_content
            # Verify .coveragerc.toml was not modified
            assert (tmp_path / ".coveragerc.toml").read_text() == (
                '[run]\nsource = ["existing"]\n'
            )

        def test_relative_files_set_to_true(self, tmp_path: Path):
            # Arrange
            (tmp_path / "pyproject.toml").write_text("""\
[project]
name = "example"
version = "0.1.0"
""")

            # Act
            with change_cwd(tmp_path), files_manager():
                CoveragePyTool().add_configs()

            # Assert
            content = (tmp_path / "pyproject.toml").read_text()
            assert "relative_files = true" in content
