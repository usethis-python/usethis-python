import pytest
import requests

from usethis._config import usethis_config
from usethis._tool.all_ import ALL_TOOLS
from usethis._tool.impl.pyproject_toml import OTHER_TOOLS, PyprojectTOMLTool


class TestOtherTools:
    def test_in_sync_with_all_tools(self):
        assert {tool.name.lower() for tool in OTHER_TOOLS} | {
            PyprojectTOMLTool().name
        } == {tool.name.lower() for tool in ALL_TOOLS}


class TestPyprojectTOMLTool:
    class TestPrintHowToUse:
        @pytest.mark.usefixtures("_vary_network_conn")
        def test_link_isnt_dead(self):
            """A regression test."""

            # Arrange
            url = (
                "https://packaging.python.org/en/latest/guides/writing-pyproject-toml/"
            )

            if not usethis_config.offline:
                # Act
                result = requests.head(url)

                # Assert
                assert result.status_code == 200

        def test_some_output(self, capfd: pytest.CaptureFixture[str]):
            # Arrange
            tool = PyprojectTOMLTool()

            # Act
            tool.print_how_to_use()

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert out

    class TestName:
        def test_value(self):
            # Arrange
            tool = PyprojectTOMLTool()

            # Act
            result = tool.name

            # Assert
            assert result == "pyproject.toml"

    class TestDevDeps:
        def test_none(self):
            # Arrange
            tool = PyprojectTOMLTool()

            # Act
            result = tool.get_dev_deps()

            # Assert
            assert result == []
