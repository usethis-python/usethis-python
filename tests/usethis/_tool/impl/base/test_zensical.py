from pathlib import Path

import pytest

from usethis._config import usethis_config
from usethis._config_file import files_manager
from usethis._test import change_cwd
from usethis._tool.impl.base.zensical import ZensicalTool
from usethis._types.backend import BackendEnum


class TestZensicalTool:
    def test_instantiate_tool(self):
        # Arrange & Act
        tool = ZensicalTool()

        # Assert
        assert isinstance(tool, ZensicalTool)

    class TestHowToUse:
        def test_print_how_to_use_uv(
            self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
        ):
            with change_cwd(tmp_path), files_manager():
                # Arrange
                tool = ZensicalTool()
                (tmp_path / "uv.lock").touch()

                # Act
                tool.print_how_to_use()

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert (
                out
                == """\
☐ Run 'uv run zensical build' to build the documentation.
☐ Run 'uv run zensical serve' to serve the documentation locally.
"""
            )

        def test_print_how_to_use_non_uv(
            self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
        ):
            with change_cwd(tmp_path), files_manager():
                # Arrange
                tool = ZensicalTool()

                # Act
                tool.print_how_to_use()

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert (
                out
                == """\
☐ Run 'zensical build' to build the documentation.
☐ Run 'zensical serve' to serve the documentation locally.
"""
            )

        def test_print_how_to_use_poetry(
            self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
        ):
            with (
                change_cwd(tmp_path),
                files_manager(),
                usethis_config.set(backend=BackendEnum.poetry),
            ):
                # Arrange
                tool = ZensicalTool()
                (tmp_path / "poetry.lock").touch()

                # Act
                tool.print_how_to_use()

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert (
                out
                == """\
☐ Run 'poetry run zensical build' to build the documentation.
☐ Run 'poetry run zensical serve' to serve the documentation locally.
"""
            )
