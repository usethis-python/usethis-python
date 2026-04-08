"""Abstract tool specification base classes."""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Protocol, final

from typing_extensions import assert_never

from usethis._config import usethis_config
from usethis._deps import is_dep_in_any_group
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._integrations.pre_commit.hooks import get_hook_ids, hook_ids_are_equivalent
from usethis._tool.config import ConfigSpec
from usethis._tool.pre_commit import PreCommitConfig
from usethis._tool.rule import RuleConfig
from usethis.errors import NoDefaultToolCommand

if TYPE_CHECKING:
    from pathlib import Path

    from usethis._file.manager import Document, KeyValueFileManager
    from usethis._integrations.pre_commit import schema as pre_commit_schema
    from usethis._tool.config import ResolutionT
    from usethis._tool.rule import Rule
    from usethis._types.deps import Dependency


@dataclass(frozen=True)
class ToolMeta:
    """These are static metadata associated with the tool.

    These aspects are independent of the current project.

    See the respective `ToolSpec` properties for each attribute for documentation on the
    individual attributes.
    """

    name: str
    managed_files: list[Path] = field(default_factory=list)
    # This is more about the inherent definition
    rule_config: RuleConfig = field(default_factory=RuleConfig)
    url: str | None = None  # For documentation purposes


class ToolSpec(Protocol, metaclass=ABCMeta):
    @property
    @abstractmethod
    def meta(self) -> ToolMeta: ...

    @final
    @property
    def name(self) -> str:
        """The name of the tool, for display purposes.

        It is assumed that this name is also the name of the Python package associated
        with the tool; if not, make sure to override methods which access this property.

        This is the display-friendly (e.g. brand compliant) name of the tool, not the
        name of a CLI command, etc. Pay mind to the correct capitalization.

        For example, the tool named `ty` has a name of `ty`, not `Ty` or `TY`.
        Import Linter has a name of `Import Linter`, not `import-linter`.
        """
        return self.meta.name

    @final
    @property
    def managed_files(self) -> list[Path]:
        """Get (relative) paths to files managed by (solely) this tool."""
        return self.meta.managed_files

    @final
    @property
    def rule_config(self) -> RuleConfig:
        """Get the linter rule configuration associated with this tool.

        This is a static, opinionated configuration which usethis uses when adding the
        tool (and managing this and other tools when adding and removing, etc.).
        """
        return self.meta.rule_config

    def preferred_file_manager(self) -> KeyValueFileManager[Document]:
        """If there is no currently active config file, this is the preferred one.

        This can vary dynamically, since often we will prefer to respect an existing
        configuration file if it exists.
        """
        return PyprojectTOMLManager()

    def config_spec(self) -> ConfigSpec:
        """Get the configuration specification for this tool.

        This can be dynamically determined, e.g. based on the source directory structure
        of the current project.

        This includes the file managers and resolution methodology.
        """
        return ConfigSpec.empty()

    def get_active_config_file_managers(
        self,
    ) -> set[KeyValueFileManager[Document]]:
        """Get file managers for all active configuration files.

        Active configuration files are just those that we expect to use based on our
        strategy for deciding on relevant files: this is a combination of the resolution
        methodology associated with the tool, and hard-coded preferences for certain
        files.

        Most commonly, this will just be a single file manager. The active config files
        themselves do not necessarily exist yet.
        """
        config_spec = self.config_spec()
        resolution = config_spec.resolution
        return self._get_active_config_file_managers_from_resolution(
            resolution,
            file_manager_by_relative_path=config_spec.file_manager_by_relative_path,
        )

    def _get_active_config_file_managers_from_resolution(
        self,
        resolution: ResolutionT,
        *,
        file_manager_by_relative_path: dict[Path, KeyValueFileManager[Document]],
    ) -> set[KeyValueFileManager[Document]]:
        if resolution == "first":
            # N.B. keep this roughly in sync with the bespoke logic for pytest
            # since that logic is based on this logic.
            for (
                relative_path,
                file_manager,
            ) in file_manager_by_relative_path.items():
                path = usethis_config.cpd() / relative_path
                if path.exists() and path.is_file():
                    return {file_manager}
        elif resolution == "first_content":
            config_spec = self.config_spec()
            for relative_path, file_manager in file_manager_by_relative_path.items():
                path = usethis_config.cpd() / relative_path
                if path.exists() and path.is_file():
                    # We check whether any of the managed config exists
                    for config_item in config_spec.config_items:
                        if config_item.root[relative_path].keys in file_manager:
                            return {file_manager}
        elif resolution == "bespoke":
            msg = (
                "The bespoke resolution method is not yet implemented for the tool "
                f"{self.name}."
            )
            raise NotImplementedError(msg)
        else:
            assert_never(resolution)

        file_managers = file_manager_by_relative_path.values()
        if not file_managers:
            return set()

        preferred_file_manager = self.preferred_file_manager()
        if preferred_file_manager not in file_managers:
            msg = (
                f"The preferred file manager '{preferred_file_manager}' is not "
                f"among the file managers '{file_managers}' for the tool "
                f"'{self.name}'."
            )
            raise NotImplementedError(msg)
        return {preferred_file_manager}

    def raw_cmd(self) -> str:
        """The default command to run the tool.

        This should not include a backend-specific prefix, e.g. don't include "uv run".

        A non-default implementation should be provided when the tool has a CLI.

        This will usually be a static string, but may involve some dynamic inference,
        e.g. when determining the source directory to operate on.

        Returns:
            The command string.

        Raises:
            NoDefaultToolCommand: If the tool has no associated command.

        Examples:
            For codespell: "codespell"
        """
        msg = f"{self.name} has no default command."
        raise NoDefaultToolCommand(msg)

    def dev_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        """The tool's development dependencies.

        These should all be considered characteristic of this particular tool.

        In general, these can vary dynamically, e.g. based on the versions of Python
        supported in the current project.

        Args:
            unconditional: Whether to return all possible dependencies regardless of
                           whether they are relevant to the current project.
        """
        return []

    def test_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        """The tool's test dependencies.

        These should all be considered characteristic of this particular tool.

        In general, these can vary dynamically, e.g. based on the versions of Python
        supported in the current project.

        Args:
            unconditional: Whether to return all possible dependencies regardless of
                           whether they are relevant to the current project.
        """
        return []

    def doc_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        """The tool's documentation dependencies.

        These should all be considered characteristic of this particular tool.

        In general, these can vary dynamically, e.g. based on the versions of Python
        supported in the current project.

        Args:
            unconditional: Whether to return all possible dependencies regardless of
                           whether they are relevant to the current project.
        """
        return []

    def deps_by_group(
        self, *, unconditional: bool = False
    ) -> dict[str, list[Dependency]]:
        """Get the characteristic dependencies of this tool, organised by group name.

        By default, this is built from dev_deps, test_deps, and doc_deps.  Override
        this method to declare dependencies in custom groups beyond those three; the
        groups that appear as keys in the returned dict are automatically discovered
        by get_dep_group_deps.

        Args:
            unconditional: Whether to return all possible dependencies regardless of
                           whether they are relevant to the current project.
        """
        result: dict[str, list[Dependency]] = {}
        for group, deps in [
            ("dev", self.dev_deps(unconditional=unconditional)),
            ("test", self.test_deps(unconditional=unconditional)),
            ("doc", self.doc_deps(unconditional=unconditional)),
        ]:
            if deps:
                result[group] = deps
        return result

    def get_dep_group_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        """Get all characteristic dependencies for the tool across all dependency groups.

        Iterates over all groups returned by deps_by_group() so that any custom groups
        declared there are automatically included.

        Args:
            unconditional: Whether to return all possible dependencies regardless of
                           whether they are relevant to the current project.
        """
        return [
            dep
            for deps in self.deps_by_group(unconditional=unconditional).values()
            for dep in deps
        ]

    def pre_commit_config(self) -> PreCommitConfig:
        """Get the pre-commit configurations for the tool.

        In general, this can vary dynamically, e.g. based on whether Ruff is being
        configured to be used as a formatter vs. a linter.
        """
        return PreCommitConfig(repo_configs=[], inform_how_to_use_on_migrate=False)

    def selected_rules(self) -> list[Rule]:
        """Get the rules managed by the tool that are currently selected.

        In general, this requires reading config files to look at which rules are
        selected for the project.
        """
        if not self.rule_config.selected:
            return []

        raise NotImplementedError

    def ignored_rules(self) -> list[Rule]:
        """Get the ignored rules managed by the tool.

        In general, this requires reading config files to look at which rules are
        ignored for the project.
        """
        if not self.rule_config.ignored:
            return []

        raise NotImplementedError

    def is_declared_as_dep(self) -> bool:
        """Whether the tool is declared as a dependency in the project.

        This is inferred based on whether any of the tools characteristic dependencies
        are declared in the project.
        """
        # N.B. currently doesn't check core dependencies nor extras.
        # Only PEP735 dependency groups.
        # See https://github.com/usethis-python/usethis-python/issues/809
        return any(
            is_dep_in_any_group(dep)
            for dep in self.get_dep_group_deps(unconditional=True)
        )

    def get_pre_commit_repos(
        self,
    ) -> list[pre_commit_schema.LocalRepo | pre_commit_schema.UriRepo]:
        """Get the pre-commit repository definitions for the tool."""
        return [c.repo for c in self.pre_commit_config().repo_configs]

    def is_pre_commit_config_present(self) -> bool:
        """Whether the tool's pre-commit configuration is present."""
        repo_configs = self.get_pre_commit_repos()

        for repo_config in repo_configs:
            if repo_config.hooks is None:
                continue

            # Check if any of the hooks are present.
            for hook in repo_config.hooks:
                if any(
                    hook_ids_are_equivalent(hook.id, hook_id)
                    for hook_id in get_hook_ids()
                ):
                    return True

        return False
