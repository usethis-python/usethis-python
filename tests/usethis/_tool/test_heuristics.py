from __future__ import annotations

from pathlib import Path

from typing_extensions import override

from usethis._config_file import files_manager
from usethis._console import how_print
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._integrations.pre_commit import schema
from usethis._test import change_cwd
from usethis._tool.base import Tool, ToolMeta
from usethis._tool.config import ConfigEntry, ConfigItem, ConfigSpec
from usethis._tool.heuristics import is_likely_used
from usethis._tool.pre_commit import PreCommitConfig


class SimpleTool(Tool):
    """Minimal tool for testing is_likely_used."""

    @property
    @override
    def meta(self) -> ToolMeta:
        return ToolMeta(name="simple_tool", managed_files=[Path("simple_tool.cfg")])

    @override
    def print_how_to_use(self) -> None:
        how_print("How to use simple_tool")

    @override
    def pre_commit_config(self) -> PreCommitConfig:
        return PreCommitConfig.from_single_repo(
            schema.UriRepo(
                repo="https://example.com/simple-tool",
                hooks=[schema.HookDefinition(id="simple-tool-hook")],
            ),
            requires_venv=False,
        )

    @override
    def config_spec(self) -> ConfigSpec:
        return ConfigSpec(
            file_manager_by_relative_path={
                Path("pyproject.toml"): PyprojectTOMLManager(),
            },
            resolution="first",
            config_items=[
                ConfigItem(
                    root={
                        Path("pyproject.toml"): ConfigEntry(
                            keys=["tool", "simple_tool"],
                            get_value=lambda: {"key": "value"},
                        )
                    }
                )
            ],
        )


class TestIsLikelyUsed:
    def test_managed_file_present(self, tmp_path: Path):
        # Arrange
        tool = SimpleTool()
        with change_cwd(tmp_path):
            (tmp_path / "simple_tool.cfg").touch()

            # Act
            result = is_likely_used(tool)

        # Assert
        assert result

    def test_managed_file_is_dir(self, tmp_path: Path):
        # Arrange
        tool = SimpleTool()
        with change_cwd(tmp_path):
            (tmp_path / "simple_tool.cfg").mkdir()

            # Act
            result = is_likely_used(tool)

        # Assert
        assert not result

    def test_config_spec_present(self, uv_init_dir: Path):
        # Arrange
        tool = SimpleTool()
        with change_cwd(uv_init_dir), files_manager():
            PyprojectTOMLManager().set_value(
                keys=["tool", "simple_tool", "key"], value="value"
            )

            # Act
            result = is_likely_used(tool)

        # Assert
        assert result

    def test_nothing_present(self, uv_init_dir: Path):
        # Arrange
        tool = SimpleTool()

        # Act
        with change_cwd(uv_init_dir), files_manager():
            result = is_likely_used(tool)

        # Assert
        assert not result

    def test_empty_config_spec(self, tmp_path: Path):
        # Arrange - a tool with empty config spec
        class EmptyConfigTool(Tool):
            @property
            @override
            def meta(self) -> ToolMeta:
                return ToolMeta(name="empty_tool")

            @override
            def print_how_to_use(self) -> None:
                how_print("How to use empty_tool")

        tool = EmptyConfigTool()

        # Act
        with change_cwd(tmp_path):
            result = is_likely_used(tool)

        # Assert
        assert not result


class TestConfigSpecIsPresent:
    def test_unmanaged_item_not_detected(self, uv_init_dir: Path):
        # An unmanaged config item is skipped even when its keys exist on disk.
        with change_cwd(uv_init_dir), files_manager():
            PyprojectTOMLManager().set_value(
                keys=["tool", "simple_tool", "key"], value="value"
            )
            spec = ConfigSpec(
                file_manager_by_relative_path={
                    Path("pyproject.toml"): PyprojectTOMLManager(),
                },
                resolution="first",
                config_items=[
                    ConfigItem(
                        managed=False,
                        root={
                            Path("pyproject.toml"): ConfigEntry(
                                keys=["tool", "simple_tool"],
                            )
                        },
                    )
                ],
            )

            # Act
            result = spec.is_present()

        # Assert
        assert not result
