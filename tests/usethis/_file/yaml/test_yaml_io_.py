import re
from pathlib import Path

import pytest
import yamltrip
from typing_extensions import override

from _test import change_cwd
from usethis._file.yaml.errors import (
    UnexpectedYAMLIOError,
    UnexpectedYAMLOpenError,
    UnexpectedYAMLValueError,
    YAMLDecodeError,
    YAMLNotFoundError,
    YAMLValueAlreadySetError,
    YAMLValueMissingError,
)
from usethis._file.yaml.io_ import YAMLDocument, YAMLFileManager


class TestYAMLFileManager:
    def test_instantiate(self):
        # Arrange
        class MyYAMLFileManager(YAMLFileManager):
            @property
            @override
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
                @override
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
                @override
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
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            # Create a sample YAML file
            (tmp_path / "my_yaml_file.yaml").write_text("key: value")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                # Act
                manager.read_file()

                # Assert
                assert isinstance(manager._content, YAMLDocument)

        def test_empty_file(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").touch()

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                # Act
                manager.read_file()

                # Assert
                assert isinstance(manager._content, YAMLDocument)

        def test_file_not_found(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
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
                @override
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
                @override
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

    class TestWriteFile:
        def test_no_cosmetic_changes(self, tmp_path: Path):
            """Reading a YAML file and exiting the manager should not modify it."""

            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            original = "key: 'value'\n"
            (tmp_path / "my_yaml_file.yaml").write_text(original)

            # Act - only read, no modifications
            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.get()  # Trigger a read without making structural changes

            # Assert - file should be unchanged
            assert (tmp_path / "my_yaml_file.yaml").read_text() == original

        def test_structural_changes_written(self, tmp_path: Path):
            """Structural changes should still be written."""

            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("key: value\n")

            # Act - make a structural change
            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.set_value(keys=["new_key"], value="new_value")

            # Assert - file should contain the new value
            contents = (tmp_path / "my_yaml_file.yaml").read_text()
            assert "new_key" in contents

    class TestDumpContent:
        def test_dump_content(self):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            my_yaml_manager = MyYAMLFileManager()
            my_yaml_manager._content = YAMLDocument(
                doc=yamltrip.loads("key: value\n"),
            )

            # Act
            result = my_yaml_manager._dump_content()

            # Assert
            assert result == "key: value\n"

        def test_none_content(self):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            my_yaml_manager = MyYAMLFileManager()
            my_yaml_manager._content = None

            # Act, Assert
            with pytest.raises(ValueError, match=r"Content is None, cannot dump."):
                my_yaml_manager._dump_content()

    class TestParseContent:
        def test_parse_content(self):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            my_yaml_manager = MyYAMLFileManager()
            content = "key: value"

            # Act
            parsed_content = my_yaml_manager._parse_content(content)

            # Assert
            assert isinstance(parsed_content, YAMLDocument)
            assert parsed_content.doc["key"] == "value"

    class TestValidateLock:
        def test_unexpected_io(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
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
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("key: value")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act, Assert
                assert manager.__contains__(["key"])

        def test_empty_file_no_keys(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").touch()

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act, Assert
                assert manager.__contains__([])

        def test_empty_file_key_missing(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").touch()

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act, Assert
                assert not manager.__contains__(["key"])

        def test_single_map_two_keys(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
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
                @override
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
                @override
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
                @override
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
                @override
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
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("key: value")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act
                value = manager[["key"]]

                # Assert
                assert value == "value"

        def test_empty_file(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").touch()

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act, Assert
                assert manager[[]] == {}

        def test_empty_keys(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
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
                @override
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
                @override
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
                @override
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
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").touch()

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                # Act
                manager.set_value(keys=[], value={"key": "value"})

                # Assert
                assert isinstance(manager._content, YAMLDocument)
                assert manager._content.doc.root == {"key": "value"}
                assert isinstance(manager._content, YAMLDocument)

        def test_root_level_is_not_mapping(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("[1,2,3]")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act, Assert
                with pytest.raises(
                    UnexpectedYAMLValueError,
                    match=r"Root level configuration must be a mapping.",
                ):
                    manager.set_value(keys=["key"], value="value")

        def test_success(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("key: value")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act
                manager.set_value(keys=["key"], value="new_value", exists_ok=True)

                # Assert
                assert isinstance(manager._content, YAMLDocument)
                assert manager._content.doc.root == {"key": "new_value"}

        def test_key_doesnt_exist_yet(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("key: value")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act
                manager.set_value(keys=["new_key"], value="new_value", exists_ok=True)

                # Assert
                assert isinstance(manager._content, YAMLDocument)
                assert manager._content.doc.root == {
                    "key": "value",
                    "new_key": "new_value",
                }

        def test_clash_with_non_mapping(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
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
                    match=r"Configuration value 'outer.inner' is already set.",
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
                @override
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
                    match=r"Configuration value 'outer' is already set.",
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
                @override
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
                assert manager._content.doc.root == {"outer": {"inner": "new_value"}}

        def test_already_exists(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("key: value")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act, Assert
                with pytest.raises(
                    YAMLValueAlreadySetError,
                    match=r"Configuration value 'key' is already set.",
                ):
                    manager.set_value(keys=["key"], value="new_value", exists_ok=False)

        def test_no_keys_non_mapping_value(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").touch()

            with (
                change_cwd(tmp_path),
                MyYAMLFileManager() as manager,
                pytest.raises(
                    UnexpectedYAMLValueError,
                    match=r"Root level configuration must be a mapping.",
                ),
            ):
                # Act, Assert
                manager.set_value(keys=[], value="not_a_dict")

        def test_no_keys_already_exists(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("key: value")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act, Assert
                with pytest.raises(
                    YAMLValueAlreadySetError,
                    match=r"Configuration value 'key' is already set.",
                ):
                    manager.set_value(keys=[], value={"key": "other"}, exists_ok=False)

        def test_keys_on_empty_doc(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("  \n")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act
                manager.set_value(keys=["key"], value="value", exists_ok=False)

                # Assert
                assert isinstance(manager._content, YAMLDocument)
                assert manager._content.doc.root == {"key": "value"}

        def test_regex_key_raises(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("key: value")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act, Assert
                with pytest.raises(
                    NotImplementedError,
                    match=r"Regex-based keys are not currently supported",
                ):
                    manager.set_value(
                        keys=[re.compile("key")], value="val", exists_ok=False
                    )

        def test_complex_value_on_empty_doc(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("  \n")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act
                manager.set_value(
                    keys=["items"],
                    value=["a", "b"],
                    exists_ok=False,
                )

                # Assert
                assert isinstance(manager._content, YAMLDocument)
                assert manager._content.doc.root == {"items": ["a", "b"]}

        def test_complex_value_clash_with_non_mapping(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("outer: value\n")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act, Assert
                with pytest.raises(
                    YAMLValueAlreadySetError,
                    match=r"Configuration value 'outer' is already set.",
                ):
                    manager.set_value(
                        keys=["outer", "inner"],
                        value=["a", "b"],
                        exists_ok=False,
                    )

        def test_complex_value_clash_overwrite(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("outer: value\n")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act
                manager.set_value(
                    keys=["outer", "inner"],
                    value=["a", "b"],
                    exists_ok=True,
                )

                # Assert
                assert isinstance(manager._content, YAMLDocument)
                assert manager._content.doc.root == {"outer": {"inner": ["a", "b"]}}

    class TestDelItem:
        def test_delete_single_item(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("key: value\nkey1: value1")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act
                del manager[["key"]]

                # Assert
                assert isinstance(manager._content, YAMLDocument)
                assert manager._content.doc.root == {"key1": "value1"}

        def test_empty_sections_removed(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
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
                assert manager._content.doc.root == {"other": "value"}

        def test_file_not_found(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
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
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("[1,2,3]")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act, Assert
                with pytest.raises(
                    YAMLValueMissingError,
                    match=r"Configuration value 'key' is missing.",
                ):
                    del manager[["key"]]

        def test_key_missing(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("key: value")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act, Assert
                with pytest.raises(
                    YAMLValueMissingError,
                    match=r"Configuration value 'non_existent_key' is missing.",
                ):
                    del manager[["non_existent_key"]]

        def test_key_wrong_dtype(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
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
                    match=r"Configuration value 'outer.key' is missing.",
                ):
                    del manager[["outer", "key"]]

        def test_delete_root_of_document(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("key: value")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act
                del manager[[]]

                # Assert
                assert isinstance(manager._content, YAMLDocument)
                assert manager._content.doc.dumps().strip() == ""

        def test_delete_root_empty_doc(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("  \n")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act, Assert
                with pytest.raises(
                    YAMLValueMissingError,
                    match=r"Configuration value '' is missing.",
                ):
                    del manager[[]]

        def test_delete_root_scalar_doc(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("hello")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act, Assert
                with pytest.raises(
                    YAMLValueMissingError,
                    match=r"Configuration value '' is missing.",
                ):
                    del manager[[]]

    class TestExtendList:
        def test_success(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("items:\n  - item1\n  - item2")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act
                manager.extend_list(keys=["items"], values=["item3", "item4"])

                # Assert
                assert isinstance(manager._content, YAMLDocument)
                assert manager._content.doc.root == {
                    "items": ["item1", "item2", "item3", "item4"]
                }

        def test_root_level_is_not_mapping(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("[1,2,3]")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act, Assert
                with pytest.raises(
                    UnexpectedYAMLValueError,
                    match=r"Root level configuration must be a mapping.",
                ):
                    manager.extend_list(keys=["key"], values=["value"])

        def test_no_keys_raises(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("items:\n  - item1\n  - item2")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act, Assert
                with pytest.raises(
                    ValueError, match=r"At least one ID key must be provided."
                ):
                    manager.extend_list(keys=[], values=["item3", "item4"])

        def test_non_existent_key(self, tmp_path: Path):
            """What happens when the key does not exist? We should just create the list."""

            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
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
                assert manager.get().doc.root == {
                    "items": ["item1", "item2"],
                    "non_existent_key": ["item3", "item4"],
                }

        def test_nested_keys(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
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
                assert manager._content.doc.root == {
                    "outer": {"inner": {"items": ["item1", "item2", "item3", "item4"]}}
                }

        def test_empty_doc(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("  \n")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act
                manager.extend_list(keys=["items"], values=["a", "b"])

                # Assert
                assert isinstance(manager._content, YAMLDocument)
                assert manager._content.doc.root == {"items": ["a", "b"]}

        def test_flow_sequence_fallback(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("items: [a, b]\n")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act
                manager.extend_list(keys=["items"], values=["c"])

                # Assert
                assert isinstance(manager._content, YAMLDocument)
                assert manager._content.doc.root == {"items": ["a", "b", "c"]}

        def test_extend_non_list_value(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("items: hello\n")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act
                manager.extend_list(keys=["items"], values=["c"])

                # Assert
                assert isinstance(manager._content, YAMLDocument)
                assert manager._content.doc.root == {"items": ["c"]}

        def test_scalar_root_doc(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("hello")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act, Assert
                with pytest.raises(
                    UnexpectedYAMLValueError,
                    match=r"Root level configuration must be a mapping.",
                ):
                    manager.extend_list(keys=["key"], values=["value"])

    class TestRemoveFromList:
        def test_success(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
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
                assert manager._content.doc.root == {"items": ["item1", "item3"]}

        def test_root_level_is_not_mapping(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("[1,2,3]")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act, Assert
                with pytest.raises(
                    UnexpectedYAMLValueError,
                    match=r"Root level configuration must be a mapping.",
                ):
                    manager.remove_from_list(keys=["key"], values=["value"])

        def test_no_keys_raises(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
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
                    ValueError, match=r"At least one ID key must be provided."
                ):
                    manager.remove_from_list(keys=[], values=["item2"])

        def test_non_existent_key(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
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
                assert manager._content.doc.root == {
                    "items": ["item1", "item2", "item3"]
                }

        def test_nested_keys(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
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
                assert manager._content.doc.root == {
                    "outer": {"inner": {"items": ["item1", "item3"]}}
                }

        def test_key_does_correspond_to_list(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
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
                assert manager._content.doc.root == {
                    "outer": {"inner": {"items": "item1"}}
                }

        def test_scalar_root_doc(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("hello")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act, Assert
                with pytest.raises(
                    UnexpectedYAMLValueError,
                    match=r"Root level configuration must be a mapping.",
                ):
                    manager.remove_from_list(keys=["key"], values=["value"])

        def test_empty_doc(self, tmp_path: Path):
            # Arrange
            class MyYAMLFileManager(YAMLFileManager):
                @property
                @override
                def relative_path(self) -> Path:
                    return Path("my_yaml_file.yaml")

            (tmp_path / "my_yaml_file.yaml").write_text("  \n")

            with change_cwd(tmp_path), MyYAMLFileManager() as manager:
                manager.read_file()

                # Act — empty doc has no keys, so remove_from_list is a no-op
                manager.remove_from_list(keys=["key"], values=["value"])
