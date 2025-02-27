from tomlkit import TOMLDocument

from usethis._integrations.toml.core import (
    extend_toml_list,
    remove_from_toml_list,
    remove_toml_value,
    set_toml_value,
)


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
        assert not (new_toml_document == original)  # noqa: SIM201
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
        assert not (new_toml_document == original)  # noqa: SIM201
        assert toml_document == original


class TestExtendTOMLList:
    def test_no_inplace_modifications(self):
        # Arrange
        toml_document = TOMLDocument()
        toml_document["a"] = ["b"]
        original = toml_document.copy()

        # Act
        new_toml_document = extend_toml_list(
            toml_document=toml_document, id_keys=["a"], values=["c", "d"]
        )

        # Assert
        assert not (new_toml_document == original)  # noqa: SIM201
        assert toml_document == original


class TestRemoveFromTOMLList:
    def test_no_inplace_modifications(self):
        # Arrange
        toml_document = TOMLDocument()
        toml_document["a"] = ["b", "c", "d"]
        original = toml_document.copy()

        # Act
        new_toml_document = remove_from_toml_list(
            toml_document=toml_document, id_keys=["a"], values=["c"]
        )

        # Assert
        assert not (new_toml_document == original)  # noqa: SIM201
        assert toml_document == original
