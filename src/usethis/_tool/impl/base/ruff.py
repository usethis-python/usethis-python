from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Literal, final

from pydantic import TypeAdapter, ValidationError
from typing_extensions import assert_never, override

from usethis._backend.dispatch import get_backend
from usethis._backend.uv.detect import is_uv_used
from usethis._config import usethis_config
from usethis._config_file import DotRuffTOMLManager, RuffTOMLManager
from usethis._console import how_print, tick_print
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._integrations.ci.bitbucket import schema as bitbucket_schema
from usethis._integrations.ci.bitbucket.anchor import (
    ScriptItemAnchor as BitbucketScriptItemAnchor,
)
from usethis._integrations.pre_commit import schema as pre_commit_schema
from usethis._tool.base import Tool
from usethis._tool.config import (
    ConfigEntry,
    ConfigItem,
    ConfigSpec,
    ensure_managed_file_exists,
)
from usethis._tool.impl.spec.ruff import RuffToolSpec
from usethis._tool.pre_commit import PreCommitConfig, PreCommitRepoConfig
from usethis._tool.rule import Rule
from usethis._types.backend import BackendEnum

if TYPE_CHECKING:
    from collections.abc import Sequence

    from usethis._file.manager import KeyValueFileManager
    from usethis._tool.rule import RuleConfig

_RUFF_VERSION = "v0.15.7"  # Manually bump this version when necessary


@final
class RuffTool(RuffToolSpec, Tool):
    @override
    def print_how_to_use(self) -> None:
        """Print how to use the Ruff tool."""
        self.print_how_to_use_linter()
        self.print_how_to_use_formatter()

    def print_how_to_use_linter(self) -> None:
        if not self.is_linter_used():
            return

        install_method = self.get_install_method()
        backend = get_backend()
        if install_method == "pre-commit":
            if backend is BackendEnum.uv and is_uv_used():
                how_print(
                    "Run 'uv run pre-commit run -a ruff-check' to run the Ruff linter."
                )
            elif backend in (BackendEnum.none, BackendEnum.uv):
                how_print("Run 'pre-commit run -a ruff-check' to run the Ruff linter.")
            else:
                assert_never(backend)
        elif install_method == "devdep" or install_method is None:
            if backend is BackendEnum.uv and is_uv_used():
                how_print(
                    "Run 'uv run ruff check --fix' to run the Ruff linter with autofixes."
                )
            elif backend in (BackendEnum.none, BackendEnum.uv):
                how_print(
                    "Run 'ruff check --fix' to run the Ruff linter with autofixes."
                )
            else:
                assert_never(backend)
        else:
            assert_never(install_method)

    def print_how_to_use_formatter(self) -> None:
        if not self.is_formatter_used():
            return

        install_method = self.get_install_method()
        backend = get_backend()
        if install_method == "pre-commit":
            if backend is BackendEnum.uv and is_uv_used():
                how_print(
                    "Run 'uv run pre-commit run -a ruff-format' to run the Ruff formatter."
                )
            elif backend in (BackendEnum.none, BackendEnum.uv):
                how_print(
                    "Run 'pre-commit run -a ruff-format' to run the Ruff formatter."
                )
            else:
                assert_never(backend)
        elif install_method == "devdep" or install_method is None:
            if backend is BackendEnum.uv and is_uv_used():
                how_print("Run 'uv run ruff format' to run the Ruff formatter.")
            elif backend in (BackendEnum.none, BackendEnum.uv):
                how_print("Run 'ruff format' to run the Ruff formatter.")
            else:
                assert_never(backend)
        else:
            assert_never(install_method)

    @override
    def pre_commit_config(self) -> PreCommitConfig:
        repo_configs: list[PreCommitRepoConfig] = []
        if self.is_linter_used():
            repo_configs.append(
                PreCommitRepoConfig(
                    repo=pre_commit_schema.UriRepo(
                        repo="https://github.com/astral-sh/ruff-pre-commit",
                        rev=_RUFF_VERSION,
                        hooks=[pre_commit_schema.HookDefinition(id="ruff-check")],
                    ),
                    requires_venv=False,
                ),
            )
        if self.is_formatter_used():
            repo_configs.append(
                PreCommitRepoConfig(
                    repo=pre_commit_schema.UriRepo(
                        repo="https://github.com/astral-sh/ruff-pre-commit",
                        rev=_RUFF_VERSION,
                        hooks=[pre_commit_schema.HookDefinition(id="ruff-format")],
                    ),
                    requires_venv=False,
                ),
            )
        return PreCommitConfig(
            repo_configs=repo_configs,
            inform_how_to_use_on_migrate=True,  # The pre-commit commands are not simpler than the venv-based commands
        )

    @override
    def get_bitbucket_steps(
        self, *, matrix_python: bool = True
    ) -> list[bitbucket_schema.Step]:
        backend = get_backend()

        steps: list[bitbucket_schema.Step] = []
        if self.is_linter_used():
            if backend is BackendEnum.uv:
                steps.append(
                    bitbucket_schema.Step(
                        name=f"Run {self.name}",
                        caches=["uv"],
                        script=bitbucket_schema.Script(
                            [
                                BitbucketScriptItemAnchor(name="install-uv"),
                                "uv run ruff check --fix",
                            ]
                        ),
                    )
                )
            elif backend is BackendEnum.none:
                steps.append(
                    bitbucket_schema.Step(
                        name=f"Run {self.name}",
                        script=bitbucket_schema.Script(
                            [
                                BitbucketScriptItemAnchor(name="ensure-venv"),
                                "ruff check --fix",
                            ]
                        ),
                    )
                )
            else:
                assert_never(backend)

        if self.is_formatter_used():
            if backend is BackendEnum.uv:
                steps.append(
                    bitbucket_schema.Step(
                        name=f"Run {self.name} Formatter",
                        caches=["uv"],
                        script=bitbucket_schema.Script(
                            [
                                BitbucketScriptItemAnchor(name="install-uv"),
                                "uv run ruff format",
                            ]
                        ),
                    )
                )
            elif backend is BackendEnum.none:
                steps.append(
                    bitbucket_schema.Step(
                        name=f"Run {self.name} Formatter",
                        script=bitbucket_schema.Script(
                            [
                                BitbucketScriptItemAnchor(name="ensure-venv"),
                                "ruff format",
                            ]
                        ),
                    )
                )
            else:
                assert_never(backend)

        return steps

    @override
    def selected_rules(self) -> list[Rule]:
        """Get the Ruff rules selected in the project."""
        (file_manager,) = self.get_active_config_file_managers()

        keys = self._get_select_keys(file_manager)
        try:
            rules = TypeAdapter(list[Rule]).validate_python(file_manager[keys])
        except (KeyError, FileNotFoundError, ValidationError):
            rules: list[Rule] = []

        return rules

    @override
    def ignored_rules(self) -> list[Rule]:
        """Get the Ruff rules ignored in the project."""
        (file_manager,) = self.get_active_config_file_managers()
        keys = self._get_ignore_keys(file_manager)
        try:
            rules = TypeAdapter(list[Rule]).validate_python(file_manager[keys])
        except (KeyError, FileNotFoundError, ValidationError):
            rules: list[Rule] = []

        return rules

    def ignore_rules_in_glob(self, rules: Sequence[Rule], *, glob: str) -> None:
        """Ignore Ruff rules in the project for a specific glob pattern."""
        rules = sorted(set(rules) - set(self.get_ignored_rules_in_glob(glob)))

        if not rules:
            return

        rules_str = ", ".join([f"'{rule}'" for rule in rules])
        s = "" if len(rules) == 1 else "s"

        (file_manager,) = self.get_active_config_file_managers()
        ensure_managed_file_exists(file_manager)
        tick_print(
            f"Ignoring {self.name} rule{s} {rules_str} for '{glob}' in '{file_manager.name}'."
        )
        keys = self._get_per_file_ignore_keys(file_manager, glob=glob)
        file_manager.extend_list(keys=keys, values=rules)

    def unignore_rules_in_glob(self, rules: Sequence[Rule], *, glob: str) -> None:
        """Stop ignoring Ruff rules in the project for a specific glob pattern."""
        rules = sorted(set(rules) & set(self.get_ignored_rules_in_glob(glob)))

        if not rules:
            return

        rules_str = ", ".join([f"'{rule}'" for rule in rules])
        s = "" if len(rules) == 1 else "s"

        (file_manager,) = self.get_active_config_file_managers()
        ensure_managed_file_exists(file_manager)
        tick_print(
            f"No longer ignoring {self.name} rule{s} {rules_str} for '{glob}' in '{file_manager.name}'."
        )
        keys = self._get_per_file_ignore_keys(file_manager, glob=glob)
        file_manager.remove_from_list(keys=keys, values=rules)

    def get_ignored_rules_in_glob(self, glob: str) -> list[Rule]:
        """Get the Ruff rules ignored in the project for a specific glob pattern."""
        (file_manager,) = self.get_active_config_file_managers()
        keys = self._get_per_file_ignore_keys(file_manager, glob=glob)
        try:
            rules = TypeAdapter(list[Rule]).validate_python(file_manager[keys])
        except (KeyError, FileNotFoundError, ValidationError):
            rules: list[Rule] = []

        return rules

    def apply_rule_config(self, rule_config: RuleConfig) -> None:
        """Apply the Ruff rules associated with a rule config to the project.

        Note, this will add both managed and unmanaged config.
        """
        is_selected = self.select_rules(rule_config.get_all_selected())
        is_ignored = self.ignore_rules(rule_config.get_all_ignored())

        # We don't want to spam the user with verbose messages about per-file ignores.
        # On the other hand, if we haven't displayed any messages at all, we need to
        # avoid a misleading silence, which would imply we haven't modified a file.
        # This is probably a workaround until there is more sophisticated support for
        # verbosity control.
        # https://github.com/usethis-python/usethis-python/issues/884
        with usethis_config.set(
            alert_only=(is_selected or is_ignored) or usethis_config.alert_only,
            instruct_only=(is_selected or is_ignored) or usethis_config.instruct_only,
        ):
            # Only add test-related directory ignore rules if the tests directory exists
            if (usethis_config.cpd() / "tests").exists():
                self.ignore_rules_in_glob(rule_config.tests_ignored, glob="tests/**")
                self.ignore_rules_in_glob(
                    rule_config.nontests_ignored, glob="!tests/**/*.py"
                )
                self.ignore_rules_in_glob(
                    rule_config.tests_unmanaged_ignored, glob="tests/**"
                )
                self.ignore_rules_in_glob(
                    rule_config.nontests_unmanaged_ignored, glob="!tests/**/*.py"
                )

    def remove_rule_config(self, rule_config: RuleConfig) -> None:
        """Remove the Ruff rules associated with a rule config from the project.

        Note, this will not modify unmanaged config.
        """
        self.deselect_rules(rule_config.selected)
        self.unignore_rules(rule_config.ignored)
        self.unignore_rules_in_glob(rule_config.tests_ignored, glob="tests/**")
        self.unignore_rules_in_glob(rule_config.nontests_ignored, glob="!tests/**/*.py")

    def set_docstyle(self, style: Literal["numpy", "google", "pep257"]) -> None:
        (file_manager,) = self.get_active_config_file_managers()

        keys = self._get_docstyle_keys(file_manager)
        if keys in file_manager and file_manager[keys] == style:
            # Already set properly
            return

        msg = f"Setting docstring style to '{style}' in '{file_manager.name}'."
        tick_print(msg)
        file_manager[self._get_docstyle_keys(file_manager)] = style

    def get_docstyle(self) -> Literal["numpy", "google", "pep257"] | None:
        """Get the docstring style set in the project."""
        (file_manager,) = self.get_active_config_file_managers()
        keys = self._get_docstyle_keys(file_manager)
        try:
            docstyle = TypeAdapter(str).validate_python(file_manager[keys])
        except (KeyError, FileNotFoundError, ValidationError):
            docstyle = None

        if docstyle not in ("numpy", "google", "pep257"):
            # Docstyle is not set or is invalid
            return None

        return docstyle

    def are_pydocstyle_rules_selected(self) -> bool:
        """Check if pydocstyle rules are selected in the configuration."""
        # If "ALL" is selected, or any rule whose alphabetical part is "D".
        rules = self.selected_rules()
        for rule in rules:
            if rule == "ALL":
                return True
            if self.is_pydocstyle_rule(rule):
                return True
        return False

    @staticmethod
    def is_pydocstyle_rule(rule: Rule) -> bool:
        return [d for d in rule if d.isalpha()] == ["D"]

    @override
    def _get_select_keys(self, file_manager: KeyValueFileManager[object]) -> list[str]:
        """Get the keys for the selected rules in the given file manager."""
        if isinstance(file_manager, PyprojectTOMLManager):
            return ["tool", "ruff", "lint", "select"]
        elif isinstance(file_manager, RuffTOMLManager | DotRuffTOMLManager):
            return ["lint", "select"]
        else:
            return super()._get_select_keys(file_manager)

    @override
    def _get_ignore_keys(self, file_manager: KeyValueFileManager[object]) -> list[str]:
        """Get the keys for the ignored rules in the given file manager."""
        if isinstance(file_manager, PyprojectTOMLManager):
            return ["tool", "ruff", "lint", "ignore"]
        elif isinstance(file_manager, RuffTOMLManager | DotRuffTOMLManager):
            return ["lint", "ignore"]
        else:
            return super()._get_ignore_keys(file_manager)

    def _get_per_file_ignore_keys(
        self, file_manager: KeyValueFileManager[object], *, glob: str
    ) -> list[str]:
        """Get the keys for the per-file ignored rules in the given file manager."""
        if isinstance(file_manager, PyprojectTOMLManager):
            return ["tool", "ruff", "lint", "per-file-ignores", glob]
        elif isinstance(file_manager, RuffTOMLManager | DotRuffTOMLManager):
            return ["lint", "per-file-ignores", glob]
        else:
            msg = (
                f"Unknown location for per-file ignored {self.name} rules for file manager "
                f"'{file_manager.name}' of type '{file_manager.__class__.__name__}'."
            )
            raise NotImplementedError(msg)

    def _get_docstyle_keys(
        self, file_manager: KeyValueFileManager[object]
    ) -> list[str]:
        """Get the keys for the docstyle rules in the given file manager."""
        if isinstance(file_manager, PyprojectTOMLManager):
            return ["tool", "ruff", "lint", "pydocstyle", "convention"]
        elif isinstance(file_manager, RuffTOMLManager | DotRuffTOMLManager):
            return ["lint", "pydocstyle", "convention"]
        else:
            msg = (
                f"Unknown location for {self.name} docstring style for file manager "
                f"'{file_manager.name}' of type '{file_manager.__class__.__name__}'."
            )
            raise NotImplementedError(msg)

    def is_linter_used(self) -> bool:
        """Check if the linter is used in the project.

        This assumes we already know that Ruff is used.
        """
        if self.linter_detection == "always":
            return True
        elif self.linter_detection == "never":
            return False
        elif self.linter_detection == "auto":
            pass
        else:
            assert_never(self.linter_detection)

        return self.is_linter_config_present() or (
            self.is_auto_detection and self.is_no_subtool_config_present()
        )

    def is_linter_config_present(self) -> bool:
        return ConfigSpec.from_flat(
            file_managers=[
                DotRuffTOMLManager(),
                RuffTOMLManager(),
                PyprojectTOMLManager(),
            ],
            resolution="first",
            config_items=[
                ConfigItem(
                    description="Linter Config",
                    root={
                        Path(".ruff.toml"): ConfigEntry(keys=["lint"]),
                        Path("ruff.toml"): ConfigEntry(keys=["lint"]),
                        Path("pyproject.toml"): ConfigEntry(
                            keys=["tool", "ruff", "lint"]
                        ),
                    },
                ),
            ],
        ).is_present()

    def is_formatter_used(self) -> bool:
        """Check if the formatter is used in the project.

        This assumes we already know that Ruff is used.
        """
        if self.formatter_detection == "always":
            return True
        elif self.formatter_detection == "never":
            return False
        elif self.formatter_detection == "auto":
            pass
        else:
            assert_never(self.formatter_detection)

        return self.is_formatter_config_present() or (
            self.is_auto_detection and self.is_no_subtool_config_present()
        )

    def is_formatter_config_present(self) -> bool:
        return ConfigSpec.from_flat(
            file_managers=[
                DotRuffTOMLManager(),
                RuffTOMLManager(),
                PyprojectTOMLManager(),
            ],
            resolution="first",
            config_items=[
                ConfigItem(
                    description="Formatter Config",
                    root={
                        Path(".ruff.toml"): ConfigEntry(keys=["format"]),
                        Path("ruff.toml"): ConfigEntry(keys=["format"]),
                        Path("pyproject.toml"): ConfigEntry(
                            keys=["tool", "ruff", "format"]
                        ),
                    },
                ),
            ],
        ).is_present()

    def is_no_subtool_config_present(self) -> bool:
        """Check if no subtool config is present."""
        return (
            not self.is_linter_config_present()
            and not self.is_formatter_config_present()
        )
