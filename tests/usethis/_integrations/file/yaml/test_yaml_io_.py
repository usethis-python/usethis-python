from collections import OrderedDict
from pathlib import Path

import pytest
import ruamel.yaml
from ruamel.yaml.comments import (
    CommentedMap,
    CommentedOrderedMap,
    CommentedSeq,
    CommentedSet,
    TaggedScalar,
)
from ruamel.yaml.scalarbool import ScalarBoolean
from ruamel.yaml.scalarfloat import ScalarFloat
from ruamel.yaml.scalarint import BinaryInt, HexCapsInt, HexInt, OctalInt, ScalarInt
from ruamel.yaml.scalarstring import FoldedScalarString, LiteralScalarString
from ruamel.yaml.timestamp import TimeStamp

from usethis._integrations.file.yaml.errors import (
    UnexpectedYAMLIOError,
    UnexpectedYAMLOpenError,
    UnexpectedYAMLValueError,
    YAMLDecodeError,
    YAMLNotFoundError,
    YAMLValueAlreadySetError,
    YAMLValueMissingError,
)
from usethis._integrations.file.yaml.io_ import YAMLDocument, YAMLFileManager, edit_yaml
from usethis._test import change_cwd


class TestYAMLFileManager:
    def test_instantiate(self):
        # Arrange
        class MyYAMLFileManager(YAMLFileManager):
            @property
            def relative_path(self) -> Path:
                return Path("my_yaml_file.yaml")

        # Act
        my_yaml_manager = MyYAMLFileManager()

        # Assert
        assert isinstance(my_yaml_manager, YAMLFileManager)

    class TestEnter:
        def test_success(self):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            # Act
            with MyYAMLFileManager() as manager:
                # Assert
                assert isinstance(manager, YAMLFileManager)
                assert manager._content is None

        def test_already_locked(self):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            my_yaml_manager = MyYAMLFileManager()
            my_yaml_manager.lock()

            # Act, Assert
            with pytest.raises(UnexpectedYAMLOpenError) as exc_info, my_yaml_manager:
                pass

            assert "already in use" in str(exc_info.value)

    class TestReadFile:
        def test_success(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            # Create a sample YAML file
            (tmp_path / "my_yaml_file.yaml").write_text("key: value")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                # Act
                manager.read_file()

                # Assert
                assert isinstance(manager._content, YAMLDocument)
                assert isinstance(manager._content.content, CommentedMap)

        def test_file_not_found(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("non_existent.yaml")

            # Act, Assert
            with (
                change_cwd(tmp_path),
                MyYAMLFileManager() as manager,
                pytest.raises(YAMLNotFoundError),
            ):
                manager.read_file()

        def test_double_read_fails(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("key: value")

            # Act, Assert
            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()
                with pytest.raises(UnexpectedYAMLIOError):
                    manager.read_file()

        def test_syntax_error(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("key: value: extra")

            # Act, Assert
            with (
                change_cwd(tmp_path),
                MyYAMLFileManager() as manager,
                pytest.raises(YAMLDecodeError),
            ):
                manager.read_file()

    class TestDumpContent:
        def test_dump_content(self):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            my_yaml_manager = MyYAMLFileManager()
            my_yaml_manager._content = YAMLDocument(
                content=CommentedMap({"key": "value"}),
                roundtripper=ruamel.yaml.YAML(typ="rt"),
            )

            # Act
            result = my_yaml_manager._dump_content()

            # Assert
            assert result == "key: value\n"

        def test_none_content(self):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            my_yaml_manager = MyYAMLFileManager()
            my_yaml_manager._content = None

            # Act, Assert
            with pytest.raises(ValueError, match="Content is None, cannot dump."):
                my_yaml_manager._dump_content()

    class TestParseContent:
        def test_parse_content(self):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            my_yaml_manager = MyYAMLFileManager()
            content = "key: value"

            # Act
            parsed_content = my_yaml_manager._parse_content(content)

            # Assert
            assert isinstance(parsed_content, YAMLDocument)
            assert isinstance(parsed_content.content, CommentedMap)
            assert parsed_content.content == {"key": "value"}

    class TestValidateLock:
        def test_unexpected_io(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            with (
                change_cwd(tmp_path),
                MyYAMLFileManager() as my_yaml_manager,
            ):
                my_yaml_manager.unlock()

                # Act, Assert
                with pytest.raises(UnexpectedYAMLIOError):
                    my_yaml_manager._validate_lock()

    class TestContains:
        def test_single_map(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("key: value")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act, Assert
                assert manager.__contains__(["key"])

        def test_single_map_two_keys(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("key1: value1")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act, Assert
                assert not manager.__contains__(["key1", "key2"])

        def test_empty_keys(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("key: value")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act, Assert
                assert manager.__contains__([])

        def test_non_existent_key(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("key: value")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act, Assert
                assert not manager.__contains__(["non_existent_key"])

        def test_nested_keys(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text(
                """\
outer:
    inner:
        key: value
"""
            )

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act, Assert
                assert manager.__contains__(["outer", "inner", "key"])
                assert not manager.__contains__(["outer", "inner", "non_existent_key"])

        def test_content_is_none(self):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            my_yaml_manager = MyYAMLFileManager()
            my_yaml_manager._content = None

            # Act, Assert
            assert not my_yaml_manager.__contains__(["key"])

    class TestGetItem:
        def test_single_item(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("key: value")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act
                value = manager[["key"]]

                # Assert
                assert value == "value"

        def test_empty_keys(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("key: value")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act, Assert
                assert manager[[]] == {"key": "value"}

        def test_nested_keys(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text(
                """\
outer:
    inner:
        key: value
"""
            )

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act
                value = manager[["outer", "inner", "key"]]

                # Assert
                assert value == "value"

        def test_missing_key(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("key: value")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act, Assert
                with pytest.raises(KeyError):
                    _ = manager[["non_existent_key"]]

        def test_key_missing(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("key: value")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act, Assert
                with pytest.raises(KeyError):
                    _ = manager[["key", "non_existent_key"]]

    class TestSetValue:
        def test_no_keys(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").touch()

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                # Act
                manager.set_value(keys=[], value={"key": "value"})

                # Assert
                assert isinstance(manager._content, YAMLDocument)
                assert manager._content.content == {"key": "value"}
                assert isinstance(manager._content, YAMLDocument)

        def test_root_level_is_not_mapping(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("[1,2,3]")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act, Assert
                with pytest.raises(
                    UnexpectedYAMLValueError,
                    match="Root level configuration must be a mapping.",
                ):
                    manager.set_value(keys=["key"], value="value")

        def test_success(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("key: value")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act
                manager.set_value(keys=["key"], value="new_value", exists_ok=True)

                # Assert
                assert isinstance(manager._content, YAMLDocument)
                assert manager._content.content == {"key": "new_value"}

        def test_key_doesnt_exist_yet(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("key: value")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act
                manager.set_value(keys=["new_key"], value="new_value", exists_ok=True)

                # Assert
                assert isinstance(manager._content, YAMLDocument)
                assert manager._content.content == {
                    "key": "value",
                    "new_key": "new_value",
                }

        def test_clash_with_non_mapping(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("""\
outer:
    inner: value
""")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act, Assert
                with pytest.raises(
                    YAMLValueAlreadySetError,
                    match="Configuration value 'outer.inner' is already set.",
                ):
                    manager.set_value(
                        keys=["outer", "inner", "value"],
                        value="new_value",
                        exists_ok=False,
                    )

        def test_already_exists_clash(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("""\
outer: ["inner"]
""")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act, Assert
                with pytest.raises(
                    YAMLValueAlreadySetError,
                    match="Configuration value 'outer' is already set.",
                ):
                    manager.set_value(
                        keys=["outer", "inner", "value"],
                        value="new_value",
                        exists_ok=False,
                    )

        def test_already_exists_clash_overwrite(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("""\
outer: value
""")
            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act
                manager.set_value(
                    keys=["outer", "inner"], value="new_value", exists_ok=True
                )

                # Assert
                assert isinstance(manager._content, YAMLDocument)
                assert manager._content.content == {"outer": {"inner": "new_value"}}

        def test_already_exists(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("key: value")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act, Assert
                with pytest.raises(
                    YAMLValueAlreadySetError,
                    match="Configuration value 'key' is already set.",
                ):
                    manager.set_value(keys=["key"], value="new_value", exists_ok=False)

    class TestDelItem:
        def test_delete_single_item(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("key: value\nkey1: value1")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act
                del manager[["key"]]

                # Assert
                assert isinstance(manager._content, YAMLDocument)
                assert manager._content.content == {"key1": "value1"}

        def test_empty_sections_removed(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text(
                """\
outer:
    inner:
        key: value
other: value
"""
            )

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act
                del manager[["outer", "inner", "key"]]

                # Assert
                assert isinstance(manager._content, YAMLDocument)
                assert manager._content.content == {"other": "value"}

        def test_file_not_found(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("non_existent.yaml")

            # Act, Assert
            with (
                change_cwd(tmp_path),
                MyYAMLFileManager() as manager,
            ):
                del manager[["key"]]

        def test_root_level_is_not_mapping(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("[1,2,3]")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act, Assert
                with pytest.raises(
                    YAMLValueMissingError,
                    match="Configuration value 'key' is missing.",
                ):
                    del manager[["key"]]

        def test_key_missing(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("key: value")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act, Assert
                with pytest.raises(
                    YAMLValueMissingError,
                    match="Configuration value 'non_existent_key' is missing.",
                ):
                    del manager[["non_existent_key"]]

        def test_key_wrong_dtype(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("""\
outer: value
""")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act, Assert
                with pytest.raises(
                    YAMLValueMissingError,
                    match="Configuration value 'outer.key' is missing.",
                ):
                    del manager[["outer", "key"]]

        def test_delete_root_of_document(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("key: value")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act
                del manager[[]]

                # Assert
                assert isinstance(manager._content, YAMLDocument)
                assert manager._content.content == {}

    class TestExtendList:
        def test_success(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("items:\n  - item1\n  - item2")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act
                manager.extend_list(keys=["items"], values=["item3", "item4"])

                # Assert
                assert isinstance(manager._content, YAMLDocument)
                assert manager._content.content == {
                    "items": ["item1", "item2", "item3", "item4"]
                }

        def test_root_level_is_not_mapping(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("[1,2,3]")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act, Assert
                with pytest.raises(
                    UnexpectedYAMLValueError,
                    match="Root level configuration must be a mapping.",
                ):
                    manager.extend_list(keys=["key"], values=["value"])

        def test_no_keys_raises(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("items:\n  - item1\n  - item2")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act, Assert
                with pytest.raises(
                    ValueError, match="At least one ID key must be provided."
                ):
                    manager.extend_list(keys=[], values=["item3", "item4"])

        def test_non_existent_key(self, tmp_path: Path):
            """What happens when the key does not exist? We should just create the list."""

            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("items:\n  - item1\n  - item2")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act
                manager.extend_list(
                    keys=["non_existent_key"], values=["item3", "item4"]
                )

                # Assert
                assert isinstance(manager._content, YAMLDocument)
                assert manager.get().content == {
                    "items": ["item1", "item2"],
                    "non_existent_key": ["item3", "item4"],
                }

        def test_nested_keys(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text(
                """\
outer:
    inner:
        items:
            - item1
            - item2
"""
            )

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act
                manager.extend_list(
                    keys=["outer", "inner", "items"], values=["item3", "item4"]
                )

                # Assert
                assert isinstance(manager._content, YAMLDocument)
                assert manager._content.content == {
                    "outer": {"inner": {"items": ["item1", "item2", "item3", "item4"]}}
                }

    class TestRemoveFromList:
        def test_success(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text(
                """\
items:
    - item1
    - item2
    - item3
"""
            )
            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act
                manager.remove_from_list(keys=["items"], values=["item2"])

                # Assert
                assert isinstance(manager._content, YAMLDocument)
                assert manager._content.content == {"items": ["item1", "item3"]}

        def test_root_level_is_not_mapping(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("[1,2,3]")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act, Assert
                with pytest.raises(
                    UnexpectedYAMLValueError,
                    match="Root level configuration must be a mapping.",
                ):
                    manager.remove_from_list(keys=["key"], values=["value"])

        def test_no_keys_raises(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text(
                """\
items:
    - item1
    - item2
    - item3
"""
            )
            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act, Assert
                with pytest.raises(
                    ValueError, match="At least one ID key must be provided."
                ):
                    manager.remove_from_list(keys=[], values=["item2"])

        def test_non_existent_key(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text(
                """\
items:
    - item1
    - item2
    - item3
"""
            )

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act
                manager.remove_from_list(keys=["non_existent_key"], values=["item2"])

                # Assert
                assert isinstance(manager._content, YAMLDocument)
                assert manager._content.content == {
                    "items": ["item1", "item2", "item3"]
                }

        def test_nested_keys(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text(
                """\
outer:
    inner:
        items:
            - item1
            - item2
            - item3
"""
            )

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act
                manager.remove_from_list(
                    keys=["outer", "inner", "items"], values=["item2"]
                )

                # Assert
                assert isinstance(manager._content, YAMLDocument)
                assert manager._content.content == {
                    "outer": {"inner": {"items": ["item1", "item3"]}}
                }

        def test_key_does_correspond_to_list(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text(
                """\
outer:
    inner:
        items: item1
"""
            )

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act
                manager.remove_from_list(
                    keys=["outer", "inner", "items"], values=["other_item"]
                )

                # Assert
                assert isinstance(manager._content, YAMLDocument)
                assert manager._content.content == {
                    "outer": {"inner": {"items": "item1"}}
                }


class TestEditYaml:
    class TestLiterals:
        """The list of literals is from ruamel/yaml/representer.py near the bottom"""

        def test_none(self, tmp_path: Path):
            # Arrange
            path = tmp_path / "test.yaml"
            path.write_text("hello: null")

            with edit_yaml(path) as yaml_document:  # Act
                content = yaml_document.content
                # Assert
                assert content == {"hello": None}

        def test_str(self, tmp_path: Path):
            # Arrange
            path = tmp_path / "test.yaml"
            path.write_text("hello")

            with edit_yaml(path) as yaml_document:  # Act
                content = yaml_document.content
                # Assert
                assert content == "hello"
                assert type(content) is str

        def test_literal_scalar_string(self, tmp_path: Path):
            # Arrange
            path = tmp_path / "test.yaml"
            path.write_text("""\
hello: |
    world
""")

            with edit_yaml(path) as yaml_document:  # Act
                content = yaml_document.content
                # Assert
                assert content == {"hello": "world\n"}
                assert isinstance(content, CommentedMap)
                assert type(content["hello"]) is LiteralScalarString

        def test_folded_scalar_string(self, tmp_path: Path):
            # Arrange
            path = tmp_path / "test.yaml"
            path.write_text("""\
hello: >
    world
""")
            with edit_yaml(path) as yaml_document:  # Act
                content = yaml_document.content
                # Assert
                assert content == {"hello": "world\n"}
                assert isinstance(content, CommentedMap)
                assert type(content["hello"]) is FoldedScalarString

        def test_int(self, tmp_path: Path):
            # Arrange
            path = tmp_path / "test.yaml"
            path.write_text("3")

            with edit_yaml(path) as yaml_document:  # Act
                content = yaml_document.content
                # Assert
                assert content == 3
                assert type(content) is int

        def test_float(self, tmp_path: Path):
            # Arrange
            path = tmp_path / "test.yaml"
            path.write_text("3.14")

            with edit_yaml(path) as yaml_document:  # Act
                content = yaml_document.content
                # Assert
                assert content == 3.14
                assert type(content) is ScalarFloat

        def test_scientific_notation(self, tmp_path: Path):
            # Arrange
            path = tmp_path / "test.yaml"
            path.write_text("3.14e-2")

            with edit_yaml(path) as yaml_document:  # Act
                content = yaml_document.content
                # Assert
                assert content == 3.14e-2
                assert type(content) is ScalarFloat

        def test_hex(self, tmp_path: Path):
            # Arrange
            path = tmp_path / "test.yaml"
            path.write_text("0x3")

            with edit_yaml(path) as yaml_document:  # Act
                content = yaml_document.content
                # Assert
                assert content == 3
                assert type(content) is HexInt

        def test_hex_caps(self, tmp_path: Path):
            # Arrange
            path = tmp_path / "test.yaml"
            path.write_text("0xE")

            with edit_yaml(path) as yaml_document:  # Act
                content = yaml_document.content
                # Assert
                assert content == 14
                assert type(content) is HexCapsInt

        def test_octal(self, tmp_path: Path):
            # Arrange
            path = tmp_path / "test.yaml"
            path.write_text("0o3")

            with edit_yaml(path) as yaml_document:  # Act
                content = yaml_document.content
                # Assert
                assert content == 3
                assert type(content) is OctalInt

        def test_binary(self, tmp_path: Path):
            # Arrange
            path = tmp_path / "test.yaml"
            path.write_text("0b11")

            with edit_yaml(path) as yaml_document:  # Act
                content = yaml_document.content
                # Assert
                assert content == 3
                assert type(content) is BinaryInt

        def test_scalar_int(self, tmp_path: Path):
            # Arrange
            path = tmp_path / "test.yaml"
            path.write_text("&anchor 3")

            with edit_yaml(path) as yaml_document:  # Act
                content = yaml_document.content
                # Assert
                assert content == 3
                assert type(content) is ScalarInt

        def test_bool(self, tmp_path: Path):
            # Arrange
            path = tmp_path / "test.yaml"
            path.write_text("true")

            with edit_yaml(path) as yaml_document:  # Act
                content = yaml_document.content
                # Assert
                assert content is True
                assert type(content) is bool

        def test_scalar_bool(self, tmp_path: Path):
            # Arrange
            path = tmp_path / "test.yaml"
            path.write_text("&anchor true")

            with edit_yaml(path) as yaml_document:  # Act
                content = yaml_document.content
                # Assert
                assert content
                assert type(content) is ScalarBoolean

        def test_commented_seq(self, tmp_path: Path):
            # Arrange
            path = tmp_path / "test.yaml"
            path.write_text("""\
- one
- two
""")

            with edit_yaml(path) as yaml_document:  # Act
                content = yaml_document.content
                # Assert
                assert content == ["one", "two"]
                assert type(content) is CommentedSeq

        def test_commented_set(self, tmp_path: Path):
            # Arrange
            path = tmp_path / "test.yaml"
            path.write_text("""\
!!set
  ? one
  ? two
""")

            with edit_yaml(path) as yaml_document:  # Act
                content = yaml_document.content
                # Assert
                assert content == {"one", "two"}
                assert type(content) is CommentedSet

        def test_commented_map(self, tmp_path: Path):
            # Arrange
            path = tmp_path / "test.yaml"
            path.write_text("""\
hello: world
""")

            with edit_yaml(path) as yaml_document:  # Act
                content = yaml_document.content
                # Assert
                assert content == {"hello": "world"}
                assert type(content) is CommentedMap

        def test_commented_ordered_map(self, tmp_path: Path):
            # Arrange
            path = tmp_path / "test.yaml"
            path.write_text("""\
!!omap
- hello: world
""")

            with edit_yaml(path) as yaml_document:  # Act
                content = yaml_document.content
                # Assert
                assert content == OrderedDict([("hello", "world")])
                assert type(content) is CommentedOrderedMap

        def test_tagged_scalar(self, tmp_path: Path):
            # Arrange
            path = tmp_path / "test.yaml"
            path.write_text("""\
!!custom 3
""")

            with edit_yaml(path) as yaml_document:  # Act
                content = yaml_document.content
                # Assert
                assert type(content) is TaggedScalar

        def test_time_stamp(self, tmp_path: Path):
            # Arrange
            path = tmp_path / "test.yaml"
            path.write_text("2001-12-15T02:59:43.1Z")

            with edit_yaml(path) as yaml_document:  # Act
                content = yaml_document.content
                # Assert
                assert type(content) is TimeStamp

        def test_empty_document(self, tmp_path: Path):
            # Arrange
            path = tmp_path / "test.yaml"
            path.write_text("")

            with edit_yaml(path) as yaml_document:  # Act
                content = yaml_document.content
                # Assert
                assert isinstance(content, CommentedMap)
                assert len(content) == 0

    class TestRoundTrip:
        @pytest.mark.xfail(
            reason="Not providing this guarantee yet. ruamel.yaml isn't easily able to cope with perfect round-tripping"
        )
        def test_single_quote_preserved(self, tmp_path: Path):
            path = tmp_path / "x.yml"
            path.write_text(
                """\
x: 'hi'
"""
            )

            # Act
            with change_cwd(tmp_path), edit_yaml(path) as _:
                pass

            # Assert
            contents = path.read_text()
            assert (
                contents
                == """\
x: 'hi'
"""
            )

        @pytest.mark.xfail(
            reason="Not providing this guarantee yet. ruamel.yaml isn't easily able to cope with perfect round-tripping"
        )
        def test_single_quoted_preserved(self, tmp_path: Path):
            path = tmp_path / "x.yml"
            path.write_text(
                """\
x: 'hi'
"""
            )

            # Act
            with change_cwd(tmp_path), edit_yaml(path) as _:
                pass

            # Assert
            contents = path.read_text()
            assert (
                contents
                == """\
x: 'hi'
"""
            )

        def test_unquoted_preserved(self, tmp_path: Path):
            path = tmp_path / "x.yml"
            path.write_text(
                """\
x: hi
"""
            )

            # Act
            with change_cwd(tmp_path), edit_yaml(path) as _:
                pass

            # Assert
            contents = path.read_text()
            assert (
                contents
                == """\
x: hi
"""
            )

        def test_indentation_5_3(self, tmp_path: Path):
            path = tmp_path / "x.yml"
            path.write_text(
                """\
x:
  -  y:
     z:
       -  w
"""
            )

            # Act
            with change_cwd(tmp_path), edit_yaml(path) as _:
                pass

            # Assert
            contents = path.read_text()
            assert (
                contents
                == """\
x:
  -  y:
     z:
       -  w
"""
            )

    def test_no_guess_indent(self, tmp_path: Path):
        path = tmp_path / "x.yml"
        path.write_text(
            """\
x:
-    y:
     z:
     -    w
"""
        )

        # Act
        with change_cwd(tmp_path), edit_yaml(path, guess_indent=False) as _:
            pass

        # Assert
        contents = path.read_text()
        assert (
            contents
            == """\
x:
  - y:
    z:
      - w
"""
        )

    def test_invalid_indentation(self, tmp_path: Path):
        # Arrange
        (tmp_path / "x.yml").write_text(
            """\
repos:
  - repo: local
        hooks:
          - id: placeholder
"""
        )

        # Act, Assert
        with (
            change_cwd(tmp_path),
            pytest.raises(YAMLDecodeError),
            edit_yaml(tmp_path / "x.yml") as _,
        ):
            pass

    def test_incorrect_indentation(self, tmp_path: Path, capfd: pytest.CaptureFixture):
        # Arrange
        (tmp_path / "x.yml").write_text("""\
- path: / 
    backend: 
      serviceName: <service_name> 
      servicePort: <port> 
""")

        # Act
        with (
            change_cwd(tmp_path),
            pytest.raises(
                YAMLDecodeError, match=r"mapping values are not allowed here"
            ),
            edit_yaml(tmp_path / "x.yml"),
        ):
            pass

        # Assert
        # Should have a hint
        out, err = capfd.readouterr()
        assert "Hint: You may have incorrect indentation the YAML file." in out
        assert not err
