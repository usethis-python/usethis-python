from ruamel.yaml.scalarstring import LiteralScalarString

from usethis._integrations.ci.bitbucket.anchor import anchor_name_from_script_item


class TestAnchorNameFromScriptName:
    def test_extraction_success(self):
        # Arrange
        item = LiteralScalarString(value="hello", anchor="world")

        # Act
        name = anchor_name_from_script_item(item)

        # Assert
        assert name == "world"

    def test_extraction_failed(self):
        # Arrange
        item = "not an item"

        # Act
        name = anchor_name_from_script_item(item)

        # Assert
        assert name is None

    def test_no_name_to_extract(self):
        # Arrange
        item = LiteralScalarString(value="hello")

        # Act
        name = anchor_name_from_script_item(item)

        # Assert
        assert name is None
