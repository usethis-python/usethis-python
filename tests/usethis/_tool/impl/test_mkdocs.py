from usethis._tool.impl.mkdocs import MkDocsTool


class TestMkDocsTool:
    def test_instantiate_tool(self):
        # Arrange & Act
        tool = MkDocsTool()

        # Assert
        assert isinstance(tool, MkDocsTool)
