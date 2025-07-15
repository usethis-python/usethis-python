from pathlib import Path

import pytest

from usethis._config_file import files_manager
from usethis._test import change_cwd
from usethis._tool.impl.mkdocs import MkDocsTool


class TestMkDocsTool:
    def test_instantiate_tool(self):
        # Arrange & Act
        tool = MkDocsTool()

        # Assert
        assert isinstance(tool, MkDocsTool)

    class TestHowToUse:
        def test_print_how_to_use_uv(
            self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
        ):
            with change_cwd(tmp_path), files_manager():
                # Arrange
                tool = MkDocsTool()
                (tmp_path / "uv.lock").touch()

                # Act
                tool.print_how_to_use()

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert (
                out
                == """\
☐ Run 'uv run mkdocs build' to build the documentation.
☐ Run 'uv run mkdocs serve' to serve the documentation locally.
"""
            )

        def test_print_how_to_use_non_uv(
            self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
        ):
            with change_cwd(tmp_path), files_manager():
                # Arrange
                tool = MkDocsTool()

                # Act
                tool.print_how_to_use()

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert (
                out
                == """\
☐ Run 'mkdocs build' to build the documentation.
☐ Run 'mkdocs serve' to serve the documentation locally.
"""
            )
