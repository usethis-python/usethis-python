"""Base classes for tool implementations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Protocol

from typing_extensions import assert_never

from usethis._backend.dispatch import get_backend
from usethis._backend.uv.detect import is_uv_used
from usethis._backend.poetry.detect import is_poetry_used
from usethis._config import usethis_config
from usethis._console import how_print, tick_print
from usethis._deps import add_deps_to_group, remove_deps_from_group
from usethis._detect.pre_commit import is_pre_commit_used
from usethis._integrations.pre_commit.cmd_ import pre_commit_raw_cmd
from usethis._integrations.pre_commit.hooks import (
    add_repo,
    get_hook_ids,
    hook_ids_are_equivalent,
    remove_hook,
)
from usethis._tool.config import NoConfigValue, ensure_managed_file_exists
from usethis._tool.heuristics import is_likely_used
from usethis._tool.rule import reconcile_rules
from usethis._tool.spec import ToolMeta, ToolSpec
from usethis._types.backend import BackendEnum
from usethis.errors import (
    UnhandledConfigEntryError,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from usethis._file.manager import Document, KeyValueFileManager
    from usethis._file.types_ import Key
    from usethis._tool.config import ConfigItem
    from usethis._tool.rule import Rule

__all__ = ["Tool", "ToolMeta", "ToolSpec"]


class Tool(ToolSpec, Protocol):
    def print_how_to_use(self) -> None:
        """Print instructions for using the tool.

        This method is invoked after a tool is added to the project, and when using
        the --how option in the CLI.

        It is useful for tools to provide a custom implementation of this method to
        provide extra details, e.g. a word to describe what the tool does
        (e.g. "... to run {self.name} spellchecker").
        """
        how_print(f"Run '{self.how_to_use_cmd()}' to run {self.name}.")

    def how_to_use_cmd(self) -> str:
        """The command used when explaining to run the tool.

        This method returns the command string for running the tool, which varies
        based on the current backend (e.g., "uv", "none"), along with installation
        method (e.g. virtual environment/development dependency versus pre-commit).
        This is used to avoid duplication in help messages.

        Returns:
            The command string for running the tool for how-to-use instructions.

        Raises:
            NoDefaultToolCommand: If the tool has no associated command.

        Examples:
            For codespell with uv backend: "uv run codespell"
            For codespell with none backend: "codespell"
        """
        backend = get_backend()
        install_method = self.get_install_method()
        if install_method == "pre-commit":
            if backend is BackendEnum.uv and is_uv_used():
                return f"uv run {pre_commit_raw_cmd} {self.how_to_use_pre_commit_hook_id()}"
            elif backend is BackendEnum.poetry and is_poetry_used():
                return f"poetry run {pre_commit_raw_cmd} {self.how_to_use_pre_commit_hook_id()}"
            elif backend in (BackendEnum.none, BackendEnum.uv, BackendEnum.poetry):
                return f"{pre_commit_raw_cmd} {self.how_to_use_pre_commit_hook_id()}"
            else:
                assert_never(backend)
        elif install_method == "devdep" or install_method is None:
            if backend is BackendEnum.uv and is_uv_used():
                return f"uv run {self.raw_cmd()}"
            elif backend is BackendEnum.poetry and is_poetry_used():
                return f"poetry run {self.raw_cmd()}"
            elif backend in (BackendEnum.none, BackendEnum.uv, BackendEnum.poetry):
                return self.raw_cmd()
            else:
                assert_never(backend)
        else:
            assert_never(install_method)

    def how_to_use_pre_commit_hook_id(self) -> str:
        """The pre-commit hook ID to use when explaining how to run via pre-commit."""
        pre_commit_repos = self.get_pre_commit_repos()
        try:
            (pre_commit_repo,) = pre_commit_repos
        except ValueError as err:
            raise NotImplementedError from err

        hooks = pre_commit_repo.hooks

        if hooks is None:
            raise NotImplementedError

        hook_ids = [hook.id for hook in hooks]

        try:
            (hook_id,) = hook_ids
        except ValueError as err:
            raise NotImplementedError from err

        if hook_id is None:
            raise NotImplementedError

        return hook_id

    def is_used(self) -> bool:
        """Whether the tool is being used in the current project.

        Four heuristics are used by default:
        1. Whether any of the tool's managed files are present.
        2. Whether any of the tool's characteristic dependencies are declared.
        3. Whether any of the tool's managed config file sections are present.
        4. Whether any of the tool's characteristic pre-commit hooks are present.
        """
        return is_likely_used(self)

    def add_dev_deps(self) -> None:
        add_deps_to_group(self.dev_deps(), "dev")

    def remove_dev_deps(self) -> None:
        remove_deps_from_group(self.dev_deps(unconditional=True), "dev")

    def add_test_deps(self) -> None:
        add_deps_to_group(self.test_deps(), "test")

    def remove_test_deps(self) -> None:
        remove_deps_from_group(self.test_deps(unconditional=True), "test")

    def add_doc_deps(self) -> None:
        add_deps_to_group(self.doc_deps(), "doc")

    def remove_doc_deps(self) -> None:
        remove_deps_from_group(self.doc_deps(unconditional=True), "doc")

    def add_pre_commit_config(self) -> None:
        """Add the tool's pre-commit configuration.

        Only adds configuration if pre-commit is being used in the project.
        """
        # Only add pre-commit configuration if pre-commit is being used
        if not is_pre_commit_used():
            return

        repos = self.get_pre_commit_repos()

        if not repos:
            return

        # Add the config for this specific tool.
        for repo_config in repos:
            if repo_config.hooks is None:
                continue

            if len(repo_config.hooks) > 1:
                msg = "Multiple hooks in a single repo not yet supported."
                raise NotImplementedError(msg)

            for hook in repo_config.hooks:
                if not any(
                    hook_ids_are_equivalent(hook.id, hook_id)
                    for hook_id in get_hook_ids()
                ):
                    # This will remove the placeholder, if present.
                    add_repo(repo_config)

    def remove_pre_commit_repo_configs(self) -> None:
        """Remove the tool's pre-commit configuration.

        If pre-commit is disabled or if the .pre-commit-config.yaml file does not
        exist, this method has no effect.
        """
        if usethis_config.disable_pre_commit:
            return

        repo_configs = self.get_pre_commit_repos()

        if not repo_configs:
            return

        for repo_config in repo_configs:
            if repo_config.hooks is None:
                continue

            # Remove the config for this specific tool.
            for hook in repo_config.hooks:
                for other_hook_id in get_hook_ids():
                    if hook.id is not None and hook_ids_are_equivalent(
                        hook.id, other_hook_id
                    ):
                        remove_hook(hook.id)

    def migrate_config_to_pre_commit(self) -> None:
        """Migrate the tool's configuration to pre-commit."""
        if self.is_used():
            pre_commit_config = self.pre_commit_config()
            # N.B. don't need to modify dev deps
            # We're migrating, so sometimes we might need to inform the user about the
            # new way to do things.
            if pre_commit_config.inform_how_to_use_on_migrate:
                self.print_how_to_use()

    def migrate_config_from_pre_commit(self) -> None:
        """Migrate the tool's configuration from pre-commit."""
        if self.is_used():
            pre_commit_config = self.pre_commit_config()
            # N.B. don't need to modify dev deps
            # We're migrating, so sometimes we might need to inform the user about
            # the new way to do things.
            if pre_commit_config.inform_how_to_use_on_migrate:
                self.print_how_to_use()

    def is_config_present(self) -> bool:
        """Whether any of the tool's managed config sections are present."""
        return self.config_spec().is_present()

    def add_configs(self) -> None:
        """Add the tool's configuration sections.

        If the config file does not exist, it will be created.
        """
        # Principles:
        # 1. We will never add configuration to a config file that is not active.
        # 2. We will never add a child key to a new parent when an existing parent
        #    already exists, even if that parent is in another file.
        # 3. Subject to #2, we will always prefer to place config in higher-priority
        #    config files.
        # In practice, the most common resolution method is "first", in which case there
        # is only ever one active file; so principles #2 and #3 are not relevant.

        active_config_file_managers = self.get_active_config_file_managers()

        already_added = False  # Only print messages for the first added config item.
        for config_item in self.config_spec().config_items:
            with usethis_config.set(
                alert_only=already_added or usethis_config.alert_only,
                instruct_only=already_added or usethis_config.instruct_only,
            ):
                added = self._add_config_item(
                    config_item, file_managers=active_config_file_managers
                )
                if added:
                    already_added = True

    def _add_config_item(
        self,
        config_item: ConfigItem,
        *,
        file_managers: set[KeyValueFileManager[Document]],
    ) -> bool:
        """Add a specific configuration item using specified file managers.

        Args:
            config_item: The configuration item to add.
            file_managers: The set of (active) file managers to consider for adding the
                           config.

        Returns:
            Whether any config was added. Config might not be added in some cases where
            it's conditional and not applicable based on the current project state.
        """
        # This is mostly a helper method for `add_configs`.

        # Filter to just those active config file managers which can manage this
        # config
        used_file_managers = [
            file_manager
            for file_manager in file_managers
            if file_manager.path in config_item.paths
        ]
        # Validate the filter is not empty
        if not used_file_managers:
            if config_item.applies_to_all:
                msg = f"No active config file managers found for one of the '{self.name}' config items."
                raise NotImplementedError(msg)
            else:
                # Early exit; this config item is not managed by any active files
                # and explicitly declares itself not-applicable-to-all-files, so it's
                # optional, effectively. See docs for ConfigItem.applies_to_all to
                # understand the motivation for this better.
                return False

        # Now, filter the config entries associated with the item to just those
        # relevant to the active file managers
        # Usually, there will only be one such entry (since there is usually one entry
        # per file manager)
        config_entries = [
            config_item
            for relative_path, config_item in config_item.root.items()
            if relative_path
            in {file_manager.relative_path for file_manager in used_file_managers}
        ]
        # Validate the filter is not empty
        if not config_entries:
            msg = f"No config entries found for one of the '{self.name}' config items."
            raise NotImplementedError(msg)

        # Focus on the one entry
        if len(config_entries) != 1:
            msg = (
                "Adding config is not yet supported for the case of multiple "
                "active config files."
            )
            raise NotImplementedError(msg)
        (entry,) = config_entries

        if isinstance(entry.get_value(), NoConfigValue):
            # No value to add, so skip this config item.
            return False

        # Create the config files if they don't exist yet.
        # N.B. we wait to do this until after all `return False` lines to avoid
        # creating empty files unnecessarily.
        for file_manager in used_file_managers:
            if not (file_manager.path.exists() and file_manager.path.is_file()):
                tick_print(f"Writing '{file_manager.relative_path}'.")
                file_manager.path.touch(exist_ok=True)

        # Try and identify which file manager to use for adding the config, based on
        # where existing config is located and our priority order
        # The idea is that the config is located at a given key sequence (e.g.
        # ["tool", "ruff", "line-length"]), and we we will look for existing config
        # using at least a shared subset of those e.g. ["tool", "ruff"], and
        # preferentially add to the highest-priority file manager which already has
        # config at that shared key sequence.
        shared_keys: list[Key] = []
        for key in entry.keys:
            shared_keys.append(key)
            new_file_managers = [
                file_manager
                for file_manager in used_file_managers
                if shared_keys in file_manager
            ]
            if not new_file_managers:
                break
            used_file_managers = new_file_managers
        # Now, use the highest-priority file manager to add the config
        (used_file_manager, *_) = used_file_managers

        if not config_item.force and entry.keys in used_file_manager:
            # We won't overwrite, so skip if there is already a value set.
            return False

        tick_print(f"Adding {self.name} config to '{used_file_manager.relative_path}'.")
        used_file_manager[entry.keys] = entry.get_value()

        return True

    def remove_configs(self) -> None:
        """Remove the tool's configuration sections.

        Note, this does not require knowledge of the config file resolution methodology,
        since all files' configs are removed regardless of whether they are in use.
        """
        config_spec = self.config_spec()

        first_removal = True
        for config_item in config_spec.config_items:
            if not config_item.managed:
                continue

            for (
                relative_path,
                file_manager,
            ) in config_spec.file_manager_by_relative_path.items():
                if file_manager.path in config_item.paths:
                    if not (file_manager.path.exists() and file_manager.path.is_file()):
                        # This is mostly for the sake of the first_removal message
                        continue

                    entry = config_item.root[relative_path]
                    try:
                        del file_manager[entry.keys]
                    except KeyError:
                        pass
                    else:
                        if first_removal:
                            tick_print(
                                f"Removing {self.name} config from '{relative_path}'."
                            )
                            first_removal = False

    def remove_managed_files(self) -> None:
        """Remove all files managed by this tool.

        This includes any tool-specific files in the project.
        If no files exist, this method has no effect.
        """
        for file in self.managed_files:
            if (usethis_config.cpd() / file).exists() and (
                usethis_config.cpd() / file
            ).is_file():
                tick_print(f"Removing '{file}'.")
                file.unlink()

    def get_install_method(self) -> Literal["devdep", "pre-commit"] | None:
        """Infer the method used to install the tool, return None if uninstalled.

        Returns "pre-commit" if the tool is never available as a dev dependency and is
        only available as a pre-commit hook.
        """
        if self.is_declared_as_dep():
            return "devdep"

        if self.is_pre_commit_config_present():
            return "pre-commit"
        return None

    def _get_select_keys(
        self, file_manager: KeyValueFileManager[Document]
    ) -> list[str]:
        """Get the configuration keys for selected rules.

        This is optional - tools that don't support rule selection can leave this
        unimplemented and will get an UnhandledConfigEntryError if selection is attempted.

        Args:
            file_manager: The file manager being used.

        Returns:
            List of keys to access the selected rules config section.

        Raises:
            UnhandledConfigEntryError: If the file manager type is not supported.
        """
        msg = (
            f"Unknown location for selected {self.name} rules for file manager "
            f"'{file_manager.name}' of type '{file_manager.__class__.__name__}'."
        )
        raise UnhandledConfigEntryError(msg)

    def select_rules(self, rules: Sequence[Rule]) -> bool:
        """Select the rules managed by the tool.

        These rules are not validated; it is assumed they are valid rules for the tool,
        and that the tool will be able to manage them.

        Respects rule code hierarchy: if a more general rule is already selected, more
        specific rules will not be added. If a more general rule is being added, more
        specific existing rules will be removed.

        Args:
            rules: The rules to select. If any of these rules are already selected, they
                   will be skipped.

        Returns:
            True if any rules were selected, False if no rules were selected.
        """
        existing = self.selected_rules()
        reconciliation = reconcile_rules(existing=existing, incoming=list(rules))

        if reconciliation.is_noop:
            return False

        (file_manager,) = self.get_active_config_file_managers()
        ensure_managed_file_exists(file_manager)
        keys = self._get_select_keys(file_manager)

        if reconciliation.to_remove:
            remove_str = ", ".join([f"'{rule}'" for rule in reconciliation.to_remove])
            s = "" if len(reconciliation.to_remove) == 1 else "s"
            tick_print(
                f"Deselecting {self.name} rule{s} {remove_str} in '{file_manager.name}'."
            )
            file_manager.remove_from_list(keys=keys, values=reconciliation.to_remove)

        if reconciliation.to_add:
            add_str = ", ".join([f"'{rule}'" for rule in reconciliation.to_add])
            s = "" if len(reconciliation.to_add) == 1 else "s"
            tick_print(
                f"Selecting {self.name} rule{s} {add_str} in '{file_manager.name}'."
            )
            file_manager.extend_list(keys=keys, values=reconciliation.to_add)

        return True

    def _get_ignore_keys(
        self, file_manager: KeyValueFileManager[Document]
    ) -> list[str]:
        """Get the configuration keys for ignored rules.

        Args:
            file_manager: The file manager being used.

        Returns:
            List of keys to access the ignored rules config section.

        Raises:
            UnhandledConfigEntryError: If the file manager type is not supported.
        """
        msg = (
            f"Unknown location for ignored {self.name} rules for file manager "
            f"'{file_manager.name}' of type '{file_manager.__class__.__name__}'."
        )
        raise UnhandledConfigEntryError(msg)

    def ignore_rules(self, rules: Sequence[Rule]) -> bool:
        """Ignore rules managed by the tool.

        Ignoring a rule is different from deselecting it - it means that even if it
        selected, it will not take effect. See the way that Ruff configuration works to
        understand this concept in more detail.

        These rules are not validated; it is assumed they are valid rules for the tool,
        and that the tool will be able to manage them.

        Respects rule code hierarchy: if a more general rule is already ignored, more
        specific rules will not be added. If a more general rule is being added, more
        specific existing rules will be removed.

        Args:
            rules: The rules to ignore. If any of these rules are already ignored, they
                   will be skipped.

        Returns:
            True if any rules were ignored, False if no rules were ignored.
        """
        existing = self.ignored_rules()
        reconciliation = reconcile_rules(existing=existing, incoming=list(rules))

        if reconciliation.is_noop:
            return False

        (file_manager,) = self.get_active_config_file_managers()
        ensure_managed_file_exists(file_manager)
        keys = self._get_ignore_keys(file_manager)

        if reconciliation.to_remove:
            remove_str = ", ".join([f"'{rule}'" for rule in reconciliation.to_remove])
            s = "" if len(reconciliation.to_remove) == 1 else "s"
            tick_print(
                f"No longer ignoring {self.name} rule{s} {remove_str} in '{file_manager.name}'."
            )
            file_manager.remove_from_list(keys=keys, values=reconciliation.to_remove)

        if reconciliation.to_add:
            add_str = ", ".join([f"'{rule}'" for rule in reconciliation.to_add])
            s = "" if len(reconciliation.to_add) == 1 else "s"
            tick_print(
                f"Ignoring {self.name} rule{s} {add_str} in '{file_manager.name}'."
            )
            file_manager.extend_list(keys=keys, values=reconciliation.to_add)

        return True

    def unignore_rules(self, rules: list[str]) -> bool:
        """Stop ignoring rules managed by the tool.

        These rules are not validated; it is assumed they are valid rules for the tool,
        and that the tool will be able to manage them.

        Args:
            rules: The rules to unignore. If any of these rules are not ignored, they
                   will be skipped.

        Returns:
            True if any rules were unignored, False if no rules were unignored.
        """
        rules = sorted(set(rules) & set(self.ignored_rules()))

        if not rules:
            return False

        rules_str = ", ".join([f"'{rule}'" for rule in rules])
        s = "" if len(rules) == 1 else "s"

        (file_manager,) = self.get_active_config_file_managers()
        ensure_managed_file_exists(file_manager)
        tick_print(
            f"No longer ignoring {self.name} rule{s} {rules_str} in '{file_manager.name}'."
        )
        keys = self._get_ignore_keys(file_manager)
        file_manager.remove_from_list(keys=keys, values=rules)

        return True

    def deselect_rules(self, rules: Sequence[Rule]) -> bool:
        """Deselect the rules managed by the tool.

        Any rules that aren't already selected are ignored.

        Args:
            rules: The rules to deselect. If any of these rules are not selected, they
                   will be skipped.

        Returns:
            True if any rules were deselected, False if no rules were deselected.
        """
        rules = sorted(set(rules) & set(self.selected_rules()))

        if not rules:
            return False

        rules_str = ", ".join([f"'{rule}'" for rule in rules])
        s = "" if len(rules) == 1 else "s"

        (file_manager,) = self.get_active_config_file_managers()
        ensure_managed_file_exists(file_manager)
        tick_print(
            f"Deselecting {self.name} rule{s} {rules_str} in '{file_manager.name}'."
        )
        keys = self._get_select_keys(file_manager)
        file_manager.remove_from_list(keys=keys, values=rules)

        return True
