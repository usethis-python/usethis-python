import re
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from usethis._config_file import files_manager
from usethis._console import how_print
from usethis._deps import add_deps_to_group
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._file.setup_cfg.io_ import SetupCFGManager
from usethis._integrations.pre_commit import schema
from usethis._integrations.pre_commit.hooks import _PLACEHOLDER_ID, get_hook_ids
from usethis._io import KeyValueFileManager
from usethis._test import change_cwd
from usethis._tool.base import Tool
from usethis._tool.config import ConfigEntry, ConfigItem, ConfigSpec
from usethis._tool.pre_commit import PreCommitConfig, PreCommitRepoConfig
from usethis._tool.rule import Rule, RuleConfig
from usethis._types.deps import Dependency
from usethis.errors import UnhandledConfigEntryError


class DefaultTool(Tool):
    """An example tool for testing purposes.

    This tool has minimal non-default configuration.
    """

    @property
    def name(self) -> str:
        return "default_tool"

    def print_how_to_use(self) -> None:
        how_print("How to use default_tool")


class MyTool(Tool):
    """An example tool for testing purposes.

    This tool has maximal non-default configuration.
    """

    @property
    def name(self) -> str:
        return "my_tool"

    def print_how_to_use(self) -> None:
        how_print("How to use my_tool")

    def get_dev_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        deps = [
            Dependency(name=self.name),
            Dependency(name="black"),
            Dependency(name="flake8"),
        ]
        if unconditional:
            deps.append(Dependency(name="pytest"))
        return deps

    def get_pre_commit_config(self) -> PreCommitConfig:
        return PreCommitConfig.from_single_repo(
            schema.UriRepo(
                repo=f"repo for {self.name}",
                hooks=[schema.HookDefinition(id="deptry")],
            ),
            requires_venv=False,
        )

    def get_config_spec(self) -> ConfigSpec:
        return ConfigSpec(
            file_manager_by_relative_path={
                Path("pyproject.toml"): PyprojectTOMLManager(),
            },
            resolution="first",
            config_items=[
                ConfigItem(
                    root={
                        Path("pyproject.toml"): ConfigEntry(
                            keys=["tool", self.name], get_value=lambda: {"key": "value"}
                        )
                    }
                )
            ],
        )

    def get_rule_config(self) -> RuleConfig:
        return RuleConfig(selected=["MYRULE"])

    def get_managed_files(self) -> list[Path]:
        return [Path("mytool-config.yaml")]

    def get_managed_pyproject_keys(self) -> list[list[str]]:
        return [["tool", self.name], ["project", "classifiers"]]


class TwoHooksTool(Tool):
    @property
    def name(self) -> str:
        return "two_hooks_tool"

    def print_how_to_use(self) -> None:
        how_print("How to use two_hooks_tool")

    def get_pre_commit_config(self) -> PreCommitConfig:
        return PreCommitConfig.from_single_repo(
            schema.UriRepo(
                repo=f"repo for {self.name}",
                hooks=[
                    schema.HookDefinition(id="ruff"),
                    schema.HookDefinition(id="ruff-format"),
                ],
            ),
            requires_venv=False,
        )


class MockToolForRuleTests(Tool):
    """Mock tool for testing rule management methods."""

    def __init__(  # noqa: PLR0913
        self,
        *,
        name: str = "mocktool",
        file_manager: KeyValueFileManager | None = None,
        ignored_rules: list[Rule] | None = None,
        selected_rules: list[Rule] | None = None,
        ignore_keys: list[str] | None = None,
        select_keys: list[str] | None = None,
    ):
        self._name = name
        self._file_manager = file_manager or MagicMock()
        self._ignored_rules = ignored_rules or []
        self._selected_rules = selected_rules or []
        self._ignore_keys = ignore_keys or ["tool", "mocktool", "ignore"]
        self._select_keys = select_keys or ["tool", "mocktool", "select"]

    @property
    def name(self) -> str:
        return self._name

    def get_active_config_file_managers(self) -> set[KeyValueFileManager]:
        return {self._file_manager}

    def _get_ignore_keys(self, file_manager: KeyValueFileManager) -> list[str]:  # noqa: ARG002
        return self._ignore_keys

    def _get_select_keys(self, file_manager: KeyValueFileManager) -> list[str]:  # noqa: ARG002
        return self._select_keys

    def get_ignored_rules(self) -> list[Rule]:
        return self._ignored_rules

    def get_selected_rules(self) -> list[Rule]:
        return self._selected_rules

    def print_how_to_use(self) -> None:
        pass


class TestTool:
    class TestName:
        def test_default(self):
            tool = DefaultTool()
            assert tool.name == "default_tool"

        def test_specific(self):
            tool = MyTool()
            assert tool.name == "my_tool"

    class TestDevDeps:
        def test_default(self):
            tool = DefaultTool()
            assert tool.get_dev_deps() == []

        def test_specific(self):
            tool = MyTool()
            assert tool.get_dev_deps() == [
                Dependency(name="my_tool"),
                Dependency(name="black"),
                Dependency(name="flake8"),
            ]

    class TestPrintHowToUse:
        def test_default(self, capsys: pytest.CaptureFixture[str]):
            tool = DefaultTool()
            tool.print_how_to_use()
            captured = capsys.readouterr()
            assert captured.out == "☐ How to use default_tool\n"

        def test_specific(self, capsys: pytest.CaptureFixture[str]):
            tool = MyTool()
            tool.print_how_to_use()
            captured = capsys.readouterr()
            assert captured.out == "☐ How to use my_tool\n"

    class TestGetPreCommitRepos:
        def test_default(self):
            tool = DefaultTool()
            assert tool.get_pre_commit_repos() == []

        def test_specific(self):
            tool = MyTool()
            assert tool.get_pre_commit_repos() == [
                schema.UriRepo(
                    repo="repo for my_tool", hooks=[schema.HookDefinition(id="deptry")]
                )
            ]

    class TestGetConfigSpec:
        def test_default(self):
            # Arrange
            tool = DefaultTool()

            # Act
            config_spec = tool.get_config_spec()

            # Assert
            assert config_spec == ConfigSpec(
                file_manager_by_relative_path={},
                resolution="first",
                config_items=[],
            )

    class TestGetAssociatedRuffRules:
        def test_default(self):
            tool = DefaultTool()
            assert tool.get_rule_config() == RuleConfig()

        def test_specific(self):
            tool = MyTool()
            assert tool.get_rule_config() == RuleConfig(selected=["MYRULE"])

    class TestGetManagedFiles:
        def test_default(self):
            tool = DefaultTool()
            assert tool.get_managed_files() == []

        def test_specific(self):
            tool = MyTool()
            assert tool.get_managed_files() == [
                Path("mytool-config.yaml"),
            ]

    class TestIsUsed:
        @pytest.mark.usefixtures("_vary_network_conn")
        def test_some_deps(self, uv_init_dir: Path):
            # Arrange
            tool = MyTool()
            with change_cwd(uv_init_dir), PyprojectTOMLManager():
                add_deps_to_group(
                    [
                        Dependency(name="black"),
                    ],
                    "eggs",
                )

                # Act
                result = tool.is_used()

            # Assert
            assert result

        def test_files(self, uv_init_dir: Path):
            # Arrange
            tool = MyTool()
            with change_cwd(uv_init_dir):
                Path("mytool-config.yaml").touch()

                # Act
                result = tool.is_used()

            # Assert
            assert result

        def test_dir(self, uv_init_dir: Path):
            # Arrange
            tool = MyTool()
            with change_cwd(uv_init_dir), PyprojectTOMLManager():
                Path("mytool-config.yaml").mkdir()

                # Act
                result = tool.is_used()

            # Assert
            assert not result

        def test_pyproject(self, uv_init_dir: Path):
            # Arrange
            tool = MyTool()
            with change_cwd(uv_init_dir), PyprojectTOMLManager():
                PyprojectTOMLManager().set_value(
                    keys=["tool", "my_tool", "key"], value="value"
                )

                # Act
                result = tool.is_used()

            # Assert
            assert result

        def test_empty(self, uv_init_dir: Path):
            # Arrange
            tool = MyTool()

            # Act
            with change_cwd(uv_init_dir), PyprojectTOMLManager():
                result = tool.is_used()

            # Assert
            assert not result

        def test_dev_deps(self, uv_init_dir: Path):
            # Arrange
            tool = MyTool()

            with change_cwd(uv_init_dir), PyprojectTOMLManager():
                add_deps_to_group(
                    [
                        Dependency(name="black"),
                    ],
                    "dev",
                )

                # Act
                result = tool.is_used()

            # Assert
            assert result

        def test_test_deps(self, uv_init_dir: Path):
            # Arrange
            tool = MyTool()

            with change_cwd(uv_init_dir), PyprojectTOMLManager():
                add_deps_to_group(
                    [
                        Dependency(name="pytest"),
                    ],
                    "test",
                )

                # Act
                result = tool.is_used()

            # Assert
            assert result

        def test_not_extra_dev_deps(self, uv_init_dir: Path):
            # Arrange
            tool = MyTool()

            with change_cwd(uv_init_dir), PyprojectTOMLManager():
                add_deps_to_group(
                    [
                        Dependency(name="isort"),
                    ],
                    "test",
                )

                # Act
                result = tool.is_used()

            # Assert
            assert not result

        def test_syntax_errors_in_pyproject_toml(
            self, uv_init_dir: Path, capsys: pytest.CaptureFixture[str]
        ):
            # https://github.com/usethis-python/usethis-python/issues/483
            # Should warn that parsing pyproject.toml failed, and print the error.
            # But should continue, with the assumption that the pyproject.toml file
            # does not contain any tool-specific configuration.

            # Arrange
            tool = MyTool()
            with change_cwd(uv_init_dir), PyprojectTOMLManager():
                # Create a pyproject.toml with a syntax error
                (uv_init_dir / "pyproject.toml").write_text(
                    """\
[tool.my_tool
"""
                )

                # Act
                result = tool.is_used()

            # Assert
            assert not result
            out, err = capsys.readouterr()
            assert not err
            assert out.replace("\n", " ").replace("  ", " ") == (
                r"⚠ Failed to decode 'pyproject.toml': Unexpected character: '\n' at line 1 col 13 "
                "⚠ Assuming 'pyproject.toml' contains no evidence of my_tool being used. "
            )

        def test_syntax_errors_in_setup_cfg(
            self, uv_init_dir: Path, capsys: pytest.CaptureFixture[str]
        ):
            # A generalization of the associated test for pyproject.toml

            # Arrange
            class ThisTool(Tool):
                @property
                def name(self) -> str:
                    return "my_tool"

                def print_how_to_use(self) -> None:
                    how_print("How to use my_tool")

                def get_config_spec(self) -> ConfigSpec:
                    # Should use setup.cfg instead of pyproject.toml
                    return ConfigSpec(
                        file_manager_by_relative_path={
                            Path("setup.cfg"): SetupCFGManager(),
                        },
                        resolution="first",
                        config_items=[
                            ConfigItem(
                                root={
                                    Path("setup.cfg"): ConfigEntry(
                                        keys=["tool", self.name, "key"],
                                        get_value=lambda: "value",
                                    )
                                }
                            )
                        ],
                    )

                def preferred_file_manager(self) -> KeyValueFileManager:
                    return SetupCFGManager()

            tool = ThisTool()
            with change_cwd(uv_init_dir), SetupCFGManager():
                # Create a setup.cfg with a syntax error
                (uv_init_dir / "setup.cfg").write_text(
                    """\
[tool.my_tool
"""
                )

                # Act
                result = tool.is_used()

            # Assert
            assert not result
            out, err = capsys.readouterr()
            assert not err
            assert out == (
                "⚠ Failed to decode 'setup.cfg':\n"
                "File contains no section headers."
                "\nfile: '<string>', line: 1\n"
                r"'[tool.my_tool\n'"
                "\n⚠ Assuming 'setup.cfg' contains no evidence of my_tool being used.\n"
            )

        def test_pre_commit_config(self, uv_init_dir: Path):
            # Arrange
            tool = MyTool()
            with change_cwd(uv_init_dir), files_manager():
                # Create a pre-commit config file
                (uv_init_dir / ".pre-commit-config.yaml").write_text("""\
repos:
  - repo: local
    hooks:
      - id: deptry
""")

                # Act
                result = tool.is_used()
            # Assert
            assert result

    class TestIsDeclaredAsDep:
        def test_dev_deps(self, uv_init_dir: Path):
            # Arrange
            tool = MyTool()

            with change_cwd(uv_init_dir), PyprojectTOMLManager():
                add_deps_to_group(
                    [
                        Dependency(name="black"),
                    ],
                    "dev",
                )

                # Act
                result = tool.is_declared_as_dep()

            # Assert
            assert result

    class TestIsPreCommitConfigPresent:
        def test_no_file(self, tmp_path: Path):
            # Arrange
            tool = MyTool()

            # Act
            with change_cwd(tmp_path):
                result = tool.is_pre_commit_config_present()

            # Assert
            assert not result

        def test_config_present(self, tmp_path: Path):
            # Arrange
            tool = MyTool()

            # Create a pre-commit config file
            (tmp_path / ".pre-commit-config.yaml").write_text("""\
repos:
  - repo: local
    hooks:
      - id: deptry
""")
            # Act
            with change_cwd(tmp_path), files_manager():
                result = tool.is_pre_commit_config_present()

            # Assert
            assert result

    class TestAddPreCommitConfig:
        def test_no_repo_configs(self, uv_init_dir: Path):
            # Arrange
            class NoRepoConfigsTool(Tool):
                @property
                def name(self) -> str:
                    return "no_repo_configs_tool"

                def get_pre_commit_config(self) -> PreCommitConfig:
                    return PreCommitConfig(
                        repo_configs=[], inform_how_to_use_on_migrate=False
                    )

                def print_how_to_use(self) -> None:
                    how_print("How to use no_repo_configs_tool")

            nrc_tool = NoRepoConfigsTool()

            # Act
            with change_cwd(uv_init_dir), files_manager():
                nrc_tool.add_pre_commit_config()

                # Assert
                assert not (uv_init_dir / ".pre-commit-config.yaml").exists()

        def test_multiple_repo_configs(self, uv_init_dir: Path):
            # Arrange
            class MultiRepoTool(Tool):
                @property
                def name(self) -> str:
                    return "multi_repo_tool"

                def print_how_to_use(self) -> None:
                    how_print("How to use multi_repo_tool")

                def get_pre_commit_config(self) -> PreCommitConfig:
                    return PreCommitConfig(
                        repo_configs=[
                            PreCommitRepoConfig(
                                repo=schema.UriRepo(
                                    repo="example",
                                    hooks=[
                                        schema.HookDefinition(id="ruff"),
                                        schema.HookDefinition(id="ruff-format"),
                                    ],
                                ),
                                requires_venv=False,
                            ),
                            PreCommitRepoConfig(
                                repo=schema.UriRepo(
                                    repo="other",
                                    hooks=[
                                        schema.HookDefinition(
                                            id="deptry",
                                        )
                                    ],
                                ),
                                requires_venv=False,
                            ),
                        ],
                        inform_how_to_use_on_migrate=False,
                    )

            # To indicate that we are, in fact, using pre-commit (otherwise the
            # add-tool method is no-op
            (uv_init_dir / ".pre-commit-config.yaml").touch()

            mrt_tool = MultiRepoTool()

            # Act
            with change_cwd(uv_init_dir):
                # Currently this feature isn't implemented, so when it is this
                # with-raises block can be removed and the test no longer needs to be
                # skipped.
                with pytest.raises(NotImplementedError):
                    mrt_tool.add_pre_commit_config()
                pytest.skip("Multiple hooks in one repo not supported yet.")

                # Assert
                assert (uv_init_dir / ".pre-commit-config.yaml").exists()

                # Note that this deliberately doesn't include validate-pyproject
                # That should only be included as a default when using the
                # `use_pre_commit` interface.
                assert get_hook_ids() == ["ruff", "ruff-format", "deptry"]

        def test_file_created(self, tmp_path: Path):
            # Arrange
            tool = MyTool()

            with change_cwd(tmp_path), files_manager():
                # Ensure pre-commit is considered used
                add_deps_to_group([Dependency(name="pre-commit")], "dev")

                # Act
                tool.add_pre_commit_config()

                # Assert
                assert (tmp_path / ".pre-commit-config.yaml").exists()

        def test_file_not_created(self, tmp_path: Path):
            # Arrange
            tool = DefaultTool()

            # Act
            with change_cwd(tmp_path), files_manager():
                tool.add_pre_commit_config()

                # Assert
                assert not (tmp_path / ".pre-commit-config.yaml").exists()

        def test_add_successful(
            self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
        ):
            # Arrange
            tool = MyTool()

            with change_cwd(tmp_path), files_manager():
                # Ensure pre-commit is considered used
                add_deps_to_group([Dependency(name="pre-commit")], "dev")
                capfd.readouterr()

                # Act
                tool.add_pre_commit_config()

                # Assert
                out, err = capfd.readouterr()
                assert not err
                assert out == (
                    "✔ Writing '.pre-commit-config.yaml'.\n"
                    "✔ Adding hook 'deptry' to '.pre-commit-config.yaml'.\n"
                )
                assert "deptry" in get_hook_ids()

        def test_dont_add_if_already_present(
            self,
            tmp_path: Path,
            capfd: pytest.CaptureFixture[str],
        ):
            # Arrange
            tool = MyTool()

            # Create a pre-commit config file with one hook
            contents = """\
repos:
  - repo: local
    hooks:
      - id: deptry
        entry: echo "different now!"
"""

            (tmp_path / ".pre-commit-config.yaml").write_text(contents)

            # Act
            with change_cwd(tmp_path), files_manager():
                tool.add_pre_commit_config()

                # Assert
                out, err = capfd.readouterr()
                assert not err
                assert not out
                assert get_hook_ids() == ["deptry"]

        def test_ignore_case_sensitivity(
            self,
            tmp_path: Path,
            capfd: pytest.CaptureFixture[str],
        ):
            # Arrange
            tool = MyTool()

            # Create a pre-commit config file with one hook
            contents = """\
repos:
  - repo: local
    hooks:
      - id: Deptry
        entry: echo "different now!"
"""

            (tmp_path / ".pre-commit-config.yaml").write_text(contents)

            # Act
            with change_cwd(tmp_path), files_manager():
                tool.add_pre_commit_config()

                # Assert
                out, err = capfd.readouterr()
                assert not err
                assert not out
                assert get_hook_ids() == ["Deptry"]

        def test_add_two_hooks_in_one_repo_when_one_already_exists(
            self,
            tmp_path: Path,
            capfd: pytest.CaptureFixture[str],
        ):
            # Arrange
            th_tool = TwoHooksTool()

            # Create a pre-commit config file with one of the two hooks
            (tmp_path / ".pre-commit-config.yaml").write_text("""\
repos:
  - repo: local
    hooks:
      - id: ruff
        entry: echo "different now!"
""")

            # Act
            with change_cwd(tmp_path):
                # Currently, we are expecting multiple hooks to not be supported.
                # At the point where we do support it, this with-raises block and
                # test skip can be removed - the rest of the test becomes valid.
                with pytest.raises(NotImplementedError):
                    th_tool.add_pre_commit_config()
                pytest.skip("Multiple hooks in one repo not supported yet")

                # Assert
                out, err = capfd.readouterr()
                assert not err
                assert out == (
                    "✔ Adding hook 'ruff-format' to '.pre-commit-config.yaml'.\n"
                )
                assert get_hook_ids() == ["ruff", "ruff-format"]

            assert (
                (tmp_path / ".pre-commit-config.yaml").read_text()
                == """\
repos:
  - repo: local
    hooks:
      - id: ruff-format
        entry: ruff format
      - id: ruff
        entry: echo "different now!"
"""
            )

        def test_two_hooks_one_repo(self, tmp_path: Path):
            # Arrange
            th_tool = TwoHooksTool()

            # Ensure pre-commit is considered used
            (tmp_path / ".pre-commit-config.yaml").touch()

            # Act
            with change_cwd(tmp_path), files_manager():
                # Currently, multiple hooks are not supported.
                # If we do ever support it, this with-raises block and
                # test skip can be removed. Instead, we will need to write this test.
                with pytest.raises(NotImplementedError):
                    th_tool.add_pre_commit_config()
                pytest.skip("Multiple hooks in one repo not supported yet")

    class TestRemovePreCommitRepoConfigs:
        def test_no_file_remove_none(self, tmp_path: Path):
            # Arrange
            nc_tool = DefaultTool()

            # Act
            with change_cwd(tmp_path):
                nc_tool.remove_pre_commit_repo_configs()

                # Assert
                assert not (tmp_path / ".pre-commit-config.yaml").exists()

        def test_no_file_remove_one(self, tmp_path: Path):
            # Arrange
            tool = MyTool()

            # Act
            with change_cwd(tmp_path):
                tool.remove_pre_commit_repo_configs()

                # Assert
                assert not (tmp_path / ".pre-commit-config.yaml").exists()

        def test_one_hook_remove_none(self, tmp_path: Path):
            # Arrange
            tool = DefaultTool()

            # Create a pre-commit config file with one hook
            contents = """\
repos:
  - repo: local
    hooks:
      - id: ruff-format
        entry: ruff format
"""
            (tmp_path / ".pre-commit-config.yaml").write_text(contents)

            # Act
            with change_cwd(tmp_path), files_manager():
                tool.remove_pre_commit_repo_configs()

                # Assert
                assert (tmp_path / ".pre-commit-config.yaml").exists()
                assert get_hook_ids() == ["ruff-format"]
                assert (tmp_path / ".pre-commit-config.yaml").read_text() == contents

        def test_one_hook_remove_different_one(self, tmp_path: Path):
            # Arrange
            tool = MyTool()

            # Create a pre-commit config file with one hook
            contents = """\
repos:
  - repo: local
    hooks:
      - id: ruff-format
        entry: ruff format
"""
            (tmp_path / ".pre-commit-config.yaml").write_text(contents)

            # Act
            with change_cwd(tmp_path), files_manager():
                tool.remove_pre_commit_repo_configs()

                # Assert
                assert (tmp_path / ".pre-commit-config.yaml").exists()
                assert get_hook_ids() == ["ruff-format"]
                assert (tmp_path / ".pre-commit-config.yaml").read_text() == contents

        def test_one_hook_remove_same_hook(self, tmp_path: Path):
            # Arrange
            tool = MyTool()

            # Create a pre-commit config file with one hook
            contents = """\
repos:
  - repo: local
    hooks:
      - id: deptry
        entry: deptry
"""
            (tmp_path / ".pre-commit-config.yaml").write_text(contents)

            # Act
            with change_cwd(tmp_path), files_manager():
                tool.remove_pre_commit_repo_configs()

                # Assert
                assert (tmp_path / ".pre-commit-config.yaml").exists()
                assert get_hook_ids() == [_PLACEHOLDER_ID]

        def test_two_repos_remove_same_two(self, tmp_path: Path):
            # Arrange
            class TwoRepoTool(Tool):
                @property
                def name(self) -> str:
                    return "two_repo_tool"

                def print_how_to_use(self) -> None:
                    how_print("How to use two_repo_tool")

                def get_pre_commit_config(self) -> PreCommitConfig:
                    return PreCommitConfig(
                        repo_configs=[
                            PreCommitRepoConfig(
                                repo=schema.UriRepo(
                                    repo="example",
                                    hooks=[
                                        schema.HookDefinition(id="ruff"),
                                        schema.HookDefinition(id="ruff-format"),
                                    ],
                                ),
                                requires_venv=False,
                            ),
                            PreCommitRepoConfig(
                                repo=schema.UriRepo(
                                    repo="other",
                                    hooks=[
                                        schema.HookDefinition(
                                            id="deptry",
                                        )
                                    ],
                                ),
                                requires_venv=False,
                            ),
                        ],
                        inform_how_to_use_on_migrate=False,
                    )

            tr_tool = TwoRepoTool()

            # Create a pre-commit config file with two hooks
            contents = """\
repos:
    - repo: local
      hooks:
        - id: ruff-format
          entry: ruff format
        - id: ruff
          entry: ruff check
"""

            (tmp_path / ".pre-commit-config.yaml").write_text(contents)

            # Act
            with change_cwd(tmp_path), files_manager():
                tr_tool.remove_pre_commit_repo_configs()

                # Assert
                assert (tmp_path / ".pre-commit-config.yaml").exists()
                assert get_hook_ids() == [_PLACEHOLDER_ID]

    class TestAddConfigs:
        def test_no_config(self, tmp_path: Path):
            # Arrange
            class NoConfigTool(Tool):
                @property
                def name(self) -> str:
                    return "no_config_tool"

                def print_how_to_use(self) -> None:
                    how_print("How to use no_config_tool")

            nc_tool = NoConfigTool()

            # Act
            with change_cwd(tmp_path):
                nc_tool.add_configs()

                # Assert
                assert not (tmp_path / "pyproject.toml").exists()

        def test_empty(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
            # Arrange
            class ThisTool(Tool):
                @property
                def name(self) -> str:
                    return "mytool"

                def print_how_to_use(self) -> None:
                    how_print("How to use this_tool")

                def get_config_spec(self) -> ConfigSpec:
                    return ConfigSpec(
                        file_manager_by_relative_path={
                            Path("pyproject.toml"): PyprojectTOMLManager(),
                        },
                        resolution="first",
                        config_items=[
                            ConfigItem(
                                root={
                                    Path("pyproject.toml"): ConfigEntry(
                                        keys=["tool", self.name, "key"],
                                        get_value=lambda: "value",
                                    )
                                }
                            )
                        ],
                    )

            (tmp_path / "pyproject.toml").write_text("")

            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                ThisTool().add_configs()

            # Assert
            assert (
                (tmp_path / "pyproject.toml").read_text()
                == """\
[tool.mytool]
key = "value"
"""
            )
            out, err = capfd.readouterr()
            assert not err
            assert out == "✔ Adding mytool config to 'pyproject.toml'.\n"

        def test_differing_sections(
            self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
        ):
            # https://github.com/usethis-python/usethis-python/issues/184
            # But needs the force=True argument.

            # Arrange
            class ThisTool(Tool):
                @property
                def name(self) -> str:
                    return "mytool"

                def print_how_to_use(self) -> None:
                    how_print("How to use this_tool")

                def get_config_spec(self) -> ConfigSpec:
                    return ConfigSpec(
                        file_manager_by_relative_path={
                            Path("pyproject.toml"): PyprojectTOMLManager(),
                        },
                        resolution="first",
                        config_items=[
                            ConfigItem(
                                root={
                                    Path("pyproject.toml"): ConfigEntry(
                                        keys=["tool", self.name],
                                        get_value=lambda: {
                                            "name": "Modular Design",
                                            "root_packages": ["example"],
                                        },
                                    )
                                },
                                force=True,
                            )
                        ],
                    )

            (tmp_path / "pyproject.toml").write_text(
                """\
[tool.mytool]
name = "Modular Design"
"""
            )

            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                ThisTool().add_configs()

            # Assert
            assert (
                (tmp_path / "pyproject.toml").read_text()
                == """\
[tool.mytool]
name = "Modular Design"
root_packages = ["example"]
"""
            )
            out, err = capfd.readouterr()
            assert not err
            assert out == "✔ Adding mytool config to 'pyproject.toml'.\n"

        def test_regex_config(self, tmp_path: Path):
            # Arrange
            class ThisTool(Tool):
                @property
                def name(self) -> str:
                    return "mytool"

                def print_how_to_use(self) -> None:
                    how_print("How to use this_tool")

                def get_config_spec(self) -> ConfigSpec:
                    return ConfigSpec(
                        file_manager_by_relative_path={
                            Path("setup.cfg"): SetupCFGManager(),
                        },
                        resolution="first",
                        config_items=[
                            ConfigItem(
                                root={
                                    Path("setup.cfg"): ConfigEntry(
                                        keys=["this", re.compile("section:.*")]
                                    )
                                }
                            )
                        ],
                    )

                def preferred_file_manager(self) -> KeyValueFileManager:
                    return SetupCFGManager()

            (tmp_path / "setup.cfg").touch()

            # Act
            with change_cwd(tmp_path), SetupCFGManager():
                ThisTool().add_configs()

            # Assert
            assert not (tmp_path / "setup.cfg").read_text()

    class TestRemoveConfigs:
        def test_regex_config(self, tmp_path: Path):
            # Arrange
            class ThisTool(Tool):
                @property
                def name(self) -> str:
                    return "mytool"

                def print_how_to_use(self) -> None:
                    how_print("How to use this_tool")

                def get_config_spec(self) -> ConfigSpec:
                    return ConfigSpec(
                        file_manager_by_relative_path={
                            Path("setup.cfg"): SetupCFGManager(),
                        },
                        resolution="first",
                        config_items=[
                            ConfigItem(
                                root={
                                    Path("setup.cfg"): ConfigEntry(
                                        keys=[re.compile("this:section:.*")]
                                    )
                                }
                            )
                        ],
                    )

                def preferred_file_manager(self) -> KeyValueFileManager:
                    return SetupCFGManager()

            (tmp_path / "setup.cfg").write_text("""\
[this:section:1]
key1 = value1
[this:section:2]
key2 = value2
[this:other]
key3 = value3
""")

            # Act
            with change_cwd(tmp_path), SetupCFGManager():
                ThisTool().remove_configs()

            # Assert
            assert (
                (tmp_path / "setup.cfg").read_text()
                == """\
[this:other]
key3 = value3
"""
            )

    class TestRemoveManagedFiles:
        def test_no_files(self, tmp_path: Path):
            # Arrange
            tool = DefaultTool()

            # Act
            with change_cwd(tmp_path):
                tool.remove_managed_files()

                # Assert
                assert not (tmp_path / "mytool-config.yaml").exists()

        def test_file(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
            # Arrange
            tool = MyTool()
            (tmp_path / "mytool-config.yaml").write_text("")

            # Act
            with change_cwd(tmp_path):
                tool.remove_managed_files()

                # Assert
                assert not (tmp_path / "mytool-config.yaml").exists()

            out, err = capfd.readouterr()
            assert not err
            assert out == "✔ Removing 'mytool-config.yaml'.\n"

        def test_dir_not_removed(self, tmp_path: Path):
            # Arrange
            tool = MyTool()
            (tmp_path / "mytool-config.yaml").mkdir()

            # Act
            with change_cwd(tmp_path):
                tool.remove_managed_files()

                # Assert
                assert (tmp_path / "mytool-config.yaml").exists()

    class TestIgnoreRules:
        class TestWhenRulesAreNew:
            def test_it_adds_rules_to_config(self) -> None:
                # Arrange
                file_manager = MagicMock()
                file_manager.name = "pyproject.toml"
                tool = MockToolForRuleTests(file_manager=file_manager, ignored_rules=[])

                # Act
                result = tool.ignore_rules(["E501", "F401"])

                # Assert
                assert result is True
                file_manager.extend_list.assert_called_once_with(
                    keys=["tool", "mocktool", "ignore"], values=["E501", "F401"]
                )

            def test_it_sorts_rules(self) -> None:
                # Arrange
                file_manager = MagicMock()
                tool = MockToolForRuleTests(file_manager=file_manager, ignored_rules=[])

                # Act
                tool.ignore_rules(["F401", "E501", "D100"])

                # Assert
                file_manager.extend_list.assert_called_once_with(
                    keys=["tool", "mocktool", "ignore"], values=["D100", "E501", "F401"]
                )

            def test_it_deduplicates_rules(self) -> None:
                # Arrange
                file_manager = MagicMock()
                tool = MockToolForRuleTests(file_manager=file_manager, ignored_rules=[])

                # Act
                tool.ignore_rules(["E501", "E501", "F401"])

                # Assert
                file_manager.extend_list.assert_called_once_with(
                    keys=["tool", "mocktool", "ignore"], values=["E501", "F401"]
                )

        class TestWhenSomeRulesAlreadyIgnored:
            def test_it_only_adds_new_rules(self) -> None:
                # Arrange
                file_manager = MagicMock()
                tool = MockToolForRuleTests(
                    file_manager=file_manager, ignored_rules=["E501"]
                )

                # Act
                result = tool.ignore_rules(["E501", "F401"])

                # Assert
                assert result is True
                file_manager.extend_list.assert_called_once_with(
                    keys=["tool", "mocktool", "ignore"], values=["F401"]
                )

        class TestWhenAllRulesAlreadyIgnored:
            def test_it_returns_false(self) -> None:
                # Arrange
                file_manager = MagicMock()
                tool = MockToolForRuleTests(
                    file_manager=file_manager, ignored_rules=["E501", "F401"]
                )

                # Act
                result = tool.ignore_rules(["E501", "F401"])

                # Assert
                assert result is False
                file_manager.extend_list.assert_not_called()

        class TestWhenNoRulesProvided:
            def test_it_returns_false(self) -> None:
                # Arrange
                file_manager = MagicMock()
                tool = MockToolForRuleTests(file_manager=file_manager)

                # Act
                result = tool.ignore_rules([])

                # Assert
                assert result is False
                file_manager.extend_list.assert_not_called()

    class TestUnignoreRules:
        class TestWhenRulesAreCurrentlyIgnored:
            def test_it_removes_rules_from_config(self) -> None:
                # Arrange
                file_manager = MagicMock()
                file_manager.name = "pyproject.toml"
                tool = MockToolForRuleTests(
                    file_manager=file_manager, ignored_rules=["E501", "F401", "D100"]
                )

                # Act
                result = tool.unignore_rules(["E501", "F401"])

                # Assert
                assert result is True
                file_manager.remove_from_list.assert_called_once_with(
                    keys=["tool", "mocktool", "ignore"], values=["E501", "F401"]
                )

            def test_it_sorts_rules(self) -> None:
                # Arrange
                file_manager = MagicMock()
                tool = MockToolForRuleTests(
                    file_manager=file_manager, ignored_rules=["E501", "F401", "D100"]
                )

                # Act
                tool.unignore_rules(["F401", "E501"])

                # Assert
                file_manager.remove_from_list.assert_called_once_with(
                    keys=["tool", "mocktool", "ignore"], values=["E501", "F401"]
                )

        class TestWhenSomeRulesNotIgnored:
            def test_it_only_removes_ignored_rules(self) -> None:
                # Arrange
                file_manager = MagicMock()
                tool = MockToolForRuleTests(
                    file_manager=file_manager, ignored_rules=["E501"]
                )

                # Act
                result = tool.unignore_rules(["E501", "F401"])

                # Assert
                assert result is True
                file_manager.remove_from_list.assert_called_once_with(
                    keys=["tool", "mocktool", "ignore"], values=["E501"]
                )

        class TestWhenNoRulesAreIgnored:
            def test_it_returns_false(self) -> None:
                # Arrange
                file_manager = MagicMock()
                tool = MockToolForRuleTests(file_manager=file_manager, ignored_rules=[])

                # Act
                result = tool.unignore_rules(["E501", "F401"])

                # Assert
                assert result is False
                file_manager.remove_from_list.assert_not_called()

        class TestWhenNoRulesProvided:
            def test_it_returns_false(self) -> None:
                # Arrange
                file_manager = MagicMock()
                tool = MockToolForRuleTests(
                    file_manager=file_manager, ignored_rules=["E501"]
                )

                # Act
                result = tool.unignore_rules([])

                # Assert
                assert result is False
                file_manager.remove_from_list.assert_not_called()

    class TestSelectRules:
        class TestWhenRulesAreNew:
            def test_it_adds_rules_to_config(self) -> None:
                # Arrange
                file_manager = MagicMock()
                file_manager.name = "pyproject.toml"
                tool = MockToolForRuleTests(
                    file_manager=file_manager, selected_rules=[]
                )

                # Act
                result = tool.select_rules(["E501", "F401"])

                # Assert
                assert result is True
                file_manager.extend_list.assert_called_once_with(
                    keys=["tool", "mocktool", "select"], values=["E501", "F401"]
                )

            def test_it_sorts_rules(self) -> None:
                # Arrange
                file_manager = MagicMock()
                tool = MockToolForRuleTests(
                    file_manager=file_manager, selected_rules=[]
                )

                # Act
                tool.select_rules(["F401", "E501", "D100"])

                # Assert
                file_manager.extend_list.assert_called_once_with(
                    keys=["tool", "mocktool", "select"], values=["D100", "E501", "F401"]
                )

        class TestWhenSomeRulesAlreadySelected:
            def test_it_only_adds_new_rules(self) -> None:
                # Arrange
                file_manager = MagicMock()
                tool = MockToolForRuleTests(
                    file_manager=file_manager, selected_rules=["E501"]
                )

                # Act
                result = tool.select_rules(["E501", "F401"])

                # Assert
                assert result is True
                file_manager.extend_list.assert_called_once_with(
                    keys=["tool", "mocktool", "select"], values=["F401"]
                )

        class TestWhenAllRulesAlreadySelected:
            def test_it_returns_false(self) -> None:
                # Arrange
                file_manager = MagicMock()
                tool = MockToolForRuleTests(
                    file_manager=file_manager, selected_rules=["E501", "F401"]
                )

                # Act
                result = tool.select_rules(["E501", "F401"])

                # Assert
                assert result is False
                file_manager.extend_list.assert_not_called()

        def test_tool_without_selection_support(self) -> None:
            # Arrange
            file_manager = MagicMock()
            tool = MockToolForRuleTests(file_manager=file_manager, selected_rules=[])
            # Override to simulate a tool without selection support
            tool._get_select_keys = lambda file_manager: super(  # type: ignore[method-assign]
                MockToolForRuleTests, tool
            )._get_select_keys(file_manager)

            # Act & Assert
            with pytest.raises(
                UnhandledConfigEntryError,
                match="Unknown location for selected mocktool rules",
            ):
                tool.select_rules(["E501"])

    class TestDeselectRules:
        class TestWhenRulesAreCurrentlySelected:
            def test_it_removes_rules_from_config(self) -> None:
                # Arrange
                file_manager = MagicMock()
                file_manager.name = "pyproject.toml"
                tool = MockToolForRuleTests(
                    file_manager=file_manager, selected_rules=["E501", "F401", "D100"]
                )

                # Act
                result = tool.deselect_rules(["E501", "F401"])

                # Assert
                assert result is True
                file_manager.remove_from_list.assert_called_once_with(
                    keys=["tool", "mocktool", "select"], values=["E501", "F401"]
                )

        class TestWhenSomeRulesNotSelected:
            def test_it_only_removes_selected_rules(self) -> None:
                # Arrange
                file_manager = MagicMock()
                tool = MockToolForRuleTests(
                    file_manager=file_manager, selected_rules=["E501"]
                )

                # Act
                result = tool.deselect_rules(["E501", "F401"])

                # Assert
                assert result is True
                file_manager.remove_from_list.assert_called_once_with(
                    keys=["tool", "mocktool", "select"], values=["E501"]
                )

        class TestWhenNoRulesAreSelected:
            def test_it_returns_false(self) -> None:
                # Arrange
                file_manager = MagicMock()
                tool = MockToolForRuleTests(
                    file_manager=file_manager, selected_rules=[]
                )

                # Act
                result = tool.deselect_rules(["E501", "F401"])

                # Assert
                assert result is False
                file_manager.remove_from_list.assert_not_called()

        def test_tool_without_selection_support(self) -> None:
            # Arrange
            file_manager = MagicMock()

            class MyMock(MockToolForRuleTests):
                def _get_select_keys(
                    self, file_manager: KeyValueFileManager
                ) -> list[str]:
                    return super(MockToolForRuleTests, self)._get_select_keys(
                        file_manager
                    )

            tool = MyMock(file_manager=file_manager, selected_rules=["E501"])

            # Act & Assert
            with pytest.raises(
                UnhandledConfigEntryError,
                match="Unknown location for selected mocktool rules",
            ):
                tool.deselect_rules(["E501"])

    class TestGetSelectedRules:
        def test_it_returns_empty_list_by_default(self) -> None:
            # Arrange
            tool = MockToolForRuleTests(selected_rules=[])

            # Act
            result = tool.get_selected_rules()

            # Assert
            assert result == []

        def test_it_returns_configured_rules(self) -> None:
            # Arrange
            tool = MockToolForRuleTests(selected_rules=["E501", "F401"])

            # Act
            result = tool.get_selected_rules()

            # Assert
            assert result == ["E501", "F401"]
