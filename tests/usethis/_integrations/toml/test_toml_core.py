from tomlkit import TOMLDocument

from usethis._integrations.toml.core import remove_toml_value, set_toml_value


class TestSetTOMLValue:
    def test_no_inplace_modifications(self):
        # Arrange
        toml_document = TOMLDocument()
        toml_document["a"] = "b"
        original = toml_document.copy()

        # Act
        new_toml_document = set_toml_value(
            toml_document=toml_document, id_keys=["c"], value="d"
        )

        # Assert
        assert new_toml_document != original
        assert toml_document == original


class TestRemoveTOMLValue:
    def test_no_inplace_modifications(self):
        # Arrange
        toml_document = TOMLDocument()
        toml_document["a"] = "b"
        original = toml_document.copy()

        # Act
        new_toml_document = remove_toml_value(
            toml_document=toml_document, id_keys=["a"]
        )

        # Assert
        assert new_toml_document != original
        assert toml_document == original
