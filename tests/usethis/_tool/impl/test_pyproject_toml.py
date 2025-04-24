from usethis._tool.all_ import ALL_TOOLS
from usethis._tool.impl.pyproject_toml import OTHER_TOOLS, PyprojectTOMLTool


class TestOtherTools:
    def test_in_sync_with_all_tools(self):
        assert set(OTHER_TOOLS) | {PyprojectTOMLTool()} == set(ALL_TOOLS)
