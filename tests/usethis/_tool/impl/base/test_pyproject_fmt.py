from pathlib import Path

import pytest

from _test import change_cwd
from usethis._config import usethis_config
from usethis._config_file import files_manager
from usethis._tool.impl.base.pyproject_fmt import PyprojectFmtTool
from usethis._types.backend import BackendEnum


class TestPyprojectFmtTool:
    class TestPrintHowToUse:
        def test_uv_only(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
            # Arrange
            (tmp_path / "uv.lock").touch()

            # Act
            with change_cwd(tmp_path), files_manager():
                PyprojectFmtTool().print_how_to_use()

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert out == (
                "☐ Run 'uv run pyproject-fmt pyproject.toml' to run pyproject-fmt.\n"
            )

    class TestApply:
        def test_uv_backend(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
            # Act
            with change_cwd(uv_init_dir), files_manager():
                PyprojectFmtTool().apply()

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert out == "✔ Running pyproject-fmt on 'pyproject.toml'.\n"

        def test_none_backend(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
            # Act
            with (
                change_cwd(tmp_path),
                usethis_config.set(backend=BackendEnum.none),
                files_manager(),
            ):
                PyprojectFmtTool().apply()

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert out == ""
