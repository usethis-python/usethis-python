"""Tool functions to add/remove tools to/from the project."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from typing_extensions import assert_never

from usethis._backend.dispatch import get_backend
from usethis._backend.uv.call import call_uv_subprocess
from usethis._backend.uv.lockfile import ensure_uv_lock
from usethis._config import usethis_config
from usethis._console import info_print, instruct_print, tick_print
from usethis._deps import add_deps_to_group, remove_deps_from_group
from usethis._file.pyproject_toml.valid import ensure_pyproject_validity
from usethis._init import ensure_dep_declaration_file, write_simple_requirements_txt
from usethis._integrations.mkdocs.core import add_docs_dir
from usethis._integrations.pre_commit.core import (
    install_pre_commit_hooks,
    remove_pre_commit_config,
    uninstall_pre_commit_hooks,
)
from usethis._integrations.pre_commit.errors import PreCommitInstallationError
from usethis._integrations.pre_commit.hooks import add_placeholder_hook, get_hook_ids
from usethis._integrations.pytest.core import add_pytest_dir, remove_pytest_dir
from usethis._tool.all_ import ALL_TOOLS
from usethis._tool.impl.base.codespell import CodespellTool
from usethis._tool.impl.base.coverage_py import CoveragePyTool
from usethis._tool.impl.base.deptry import DeptryTool
from usethis._tool.impl.base.import_linter import ImportLinterTool
from usethis._tool.impl.base.mkdocs import MkDocsTool
from usethis._tool.impl.base.pre_commit import PreCommitTool
from usethis._tool.impl.base.pyproject_fmt import PyprojectFmtTool
from usethis._tool.impl.base.pyproject_toml import PyprojectTOMLTool
from usethis._tool.impl.base.pytest import PytestTool
from usethis._tool.impl.base.requirements_txt import RequirementsTxtTool
from usethis._tool.impl.base.ruff import RuffTool
from usethis._tool.impl.base.ty import TyTool
from usethis._tool.rule import RuleConfig
from usethis._types.backend import BackendEnum
from usethis._types.deps import Dependency

if TYPE_CHECKING:
    from usethis._tool.all_ import SupportedToolType

# Note - all these functions invoke ensure_dep_declaratiom_file() at the start, since
# declaring dependencies in pyproject.toml requires that file to exist.


class UseToolFunc(Protocol):
    def __call__(self, *, remove: bool, how: bool) -> None:
        """A function that adds/removes a tool to/from the project.

        Args:
            remove: If True, remove the tool instead of adding it.
            how: If True, print how to use the tool instead of adding/removing it.
        """


def use_codespell(*, remove: bool = False, how: bool = False) -> None:
    """Add or remove codespell from the project."""
    tool = CodespellTool()

    if how:
        tool.print_how_to_use()
        return

    if not remove:
        ensure_dep_declaration_file()

        tool.add_dev_deps()
        tool.add_pre_commit_config()

        tool.add_configs()
        tool.print_how_to_use()
    else:
        tool.remove_configs()
        tool.remove_pre_commit_repo_configs()
        tool.remove_dev_deps()
        tool.remove_managed_files()


def use_coverage_py(*, remove: bool = False, how: bool = False) -> None:
    """Add or remove coverage.py from the project."""
    tool = CoveragePyTool()

    if how:
        tool.print_how_to_use()
        return

    if not remove:
        ensure_dep_declaration_file()

        tool.add_test_deps()
        tool.add_configs()
        tool.print_how_to_use()
    else:
        tool.remove_configs()
        tool.remove_test_deps()
        tool.remove_managed_files()


def use_deptry(*, remove: bool = False, how: bool = False) -> None:
    """Add or remove deptry from the project."""
    tool = DeptryTool()

    if how:
        tool.print_how_to_use()
        return

    if not remove:
        ensure_dep_declaration_file()

        tool.add_dev_deps()
        tool.add_pre_commit_config()

        tool.add_configs()
        tool.print_how_to_use()
    else:
        tool.remove_pre_commit_repo_configs()
        tool.remove_configs()
        tool.remove_dev_deps()
        tool.remove_managed_files()


def use_import_linter(*, remove: bool = False, how: bool = False) -> None:
    """Add or remove import-linter from the project."""
    tool = ImportLinterTool()

    if how:
        tool.print_how_to_use()
        return

    if not remove:
        ensure_dep_declaration_file()

        tool.add_dev_deps()
        tool.add_configs()
        if RuffTool().is_used():
            RuffTool().apply_rule_config(tool.rule_config)
        tool.add_pre_commit_config()

        tool.print_how_to_use()
    else:
        tool.remove_pre_commit_repo_configs()
        if RuffTool().is_used():
            RuffTool().remove_rule_config(tool.rule_config)
        tool.remove_configs()
        tool.remove_dev_deps()
        tool.remove_managed_files()


def use_mkdocs(*, remove: bool = False, how: bool = False) -> None:
    """Add or remove MkDocs from the project."""
    tool = MkDocsTool()

    if how:
        tool.print_how_to_use()
        return

    if not remove:
        ensure_dep_declaration_file()
        (usethis_config.cpd() / "mkdocs.yml").touch()

        add_docs_dir()

        tool.add_doc_deps()
        tool.add_configs()

        tool.print_how_to_use()
    else:
        # N.B. no need to remove configs because they all lie in managed files.

        tool.remove_doc_deps()
        tool.remove_managed_files()


def use_pre_commit(*, remove: bool = False, how: bool = False) -> None:
    """Add or remove pre-commit from the project."""
    tool = PreCommitTool()

    if how:
        tool.print_how_to_use()
        return

    if not remove:
        ensure_dep_declaration_file()

        tool.add_dev_deps()
        _add_all_tools_pre_commit_configs()

        for _tool in ALL_TOOLS:
            _tool.migrate_config_to_pre_commit()

        if not get_hook_ids():
            add_placeholder_hook()

        try:
            install_pre_commit_hooks()
        except PreCommitInstallationError:
            instruct_print(
                "Run 'uv run pre-commit install' to install pre-commit to Git."
            )

        tool.print_how_to_use()
    else:
        try:
            uninstall_pre_commit_hooks()
        except PreCommitInstallationError:
            instruct_print(
                "Run 'uv run pre-commit uninstall' to uninstall pre-commit from Git."
            )

        remove_pre_commit_config()
        tool.remove_dev_deps()

        for _tool in ALL_TOOLS:
            _tool.migrate_config_from_pre_commit()

        tool.remove_managed_files()


def _add_all_tools_pre_commit_configs():
    PreCommitTool().add_pre_commit_config()
    for _tool in ALL_TOOLS:
        if isinstance(_tool, PreCommitTool):
            continue
        if _tool.is_used():
            _tool.add_pre_commit_config()


def use_pyproject_fmt(*, remove: bool = False, how: bool = False) -> None:
    """Add or remove pyproject-fmt from the project."""
    tool = PyprojectFmtTool()

    if how:
        tool.print_how_to_use()
        return

    if not remove:
        ensure_dep_declaration_file()

        tool.add_dev_deps()
        tool.add_pre_commit_config()

        tool.add_configs()
        tool.print_how_to_use()
    else:
        tool.remove_configs()
        tool.remove_pre_commit_repo_configs()
        tool.remove_dev_deps()
        tool.remove_managed_files()


def use_pyproject_toml(*, remove: bool = False, how: bool = False) -> None:
    """Add or remove pyproject.toml management from the project."""
    tool = PyprojectTOMLTool()

    if how:
        tool.print_how_to_use()
        return

    if not remove:
        ensure_dep_declaration_file()

        ensure_pyproject_validity()
        tool.print_how_to_use()
    else:
        tool.remove_managed_files()


def use_pytest(*, remove: bool = False, how: bool = False) -> None:
    """Add or remove pytest from the project."""
    tool = PytestTool()

    if how:
        tool.print_how_to_use()
        return

    if not remove:
        ensure_dep_declaration_file()

        tool.add_test_deps()
        tool.add_configs()

        # deptry currently can't scan the tests folder for dev deps
        # https://github.com/fpgmaas/deptry/issues/302
        add_pytest_dir()

        rule_config = tool.rule_config

        for _tool in ALL_TOOLS:
            if isinstance(_tool, PytestTool):
                continue

            if _tool.rule_config.is_related_to_tests and _tool.is_used():
                rule_config |= _tool.rule_config.subset_related_to_tests()

        if RuffTool().is_used():
            RuffTool().apply_rule_config(rule_config)

        tool.print_how_to_use()

        if CoveragePyTool().is_used():
            CoveragePyTool().print_how_to_use()
    else:
        if RuffTool().is_used():
            RuffTool().remove_rule_config(tool.rule_config)
        tool.remove_configs()
        tool.remove_test_deps()
        remove_pytest_dir()  # Last, since this is a manual step

        if CoveragePyTool().is_used():
            CoveragePyTool().print_how_to_use()
        tool.remove_managed_files()


def use_requirements_txt(*, remove: bool = False, how: bool = False) -> None:
    """Add or remove requirements.txt management from the project."""
    tool = RequirementsTxtTool()

    if how:
        tool.print_how_to_use()
        return

    path = usethis_config.cpd() / "requirements.txt"

    if not remove:
        backend = get_backend()

        if PreCommitTool().is_used():
            # pyproject.toml is needed for config items and dependency groups
            ensure_dep_declaration_file()
            tool.add_pre_commit_config()
            tool.add_configs()
            if backend is BackendEnum.uv:
                with usethis_config.set(quiet=True):
                    add_deps_to_group([Dependency(name="uv")], "uv", default=False)

        if path.exists():
            # requirements file already exists - short circuit; only need to explain how
            # how to re-generate it.
            tool.print_how_to_use()
            return

        if backend is BackendEnum.uv:
            if not (usethis_config.cpd() / "pyproject.toml").exists():
                write_simple_requirements_txt()
            elif not usethis_config.frozen:
                ensure_uv_lock()
                tick_print("Writing 'requirements.txt'.")
                call_uv_subprocess(
                    [
                        "export",
                        "--frozen",
                        "--output-file=requirements.txt",
                    ],
                    change_toml=False,
                )
        elif backend is BackendEnum.none:
            # Simply dump the dependencies list to requirements.txt
            if usethis_config.backend is BackendEnum.auto:
                info_print(
                    "Generating 'requirements.txt' with un-pinned, abstract dependencies."
                )
                info_print(
                    "Consider installing 'uv' for pinned, cross-platform, full requirements files."
                )

            write_simple_requirements_txt()
        else:
            assert_never(backend)

        tool.print_how_to_use()
    else:
        tool.remove_pre_commit_repo_configs()
        tool.remove_configs()
        with usethis_config.set(quiet=True):
            remove_deps_from_group([Dependency(name="uv")], "uv")
        tool.remove_managed_files()


def use_ruff(
    *,
    remove: bool = False,
    how: bool = False,
    minimal: bool = False,
    linter: bool = True,
    formatter: bool = True,
) -> None:
    """Add Ruff to the project.

    By default, sensible default rules are selected if there are no rules selected yet,
    but this behaviour can be controlled by using the `minimal` option.

    If the existing rules are all pydocstyle rules (managed by the `usethis docstyle`
    interface), then the default rules will still be added, again excepting when the
    `minimal` option is used.

    Args:
        remove: Remove Ruff configuration.
        how: Print how to use Ruff.
        minimal: Don't add any default rules.
        linter: Whether to add/remove the Ruff linter.
        formatter: Whether to add/remove the Ruff formatter.
    """
    if how:
        tool = RuffTool(
            linter_detection="always" if linter else "never",
            formatter_detection="always" if formatter else "never",
        )
        tool.print_how_to_use()
        return

    # Only add ruff rules if the user doesn't already have a select/ignore list.
    # Otherwise, we should leave them alone. An exception is pydocstyle rules, since
    # these are the responsibility of the pydocstyle interface via `usethis docstyle`.
    tool = RuffTool()
    if minimal:
        rule_config = RuleConfig()
    elif (
        # See docstring. Basically, `usethis docstyle` manages the pydocstyle rules,
        # so we want to allow the user to subsequently call `usethis tool ruff` and
        # still get non-minimal default rules.
        all(tool.is_pydocstyle_rule(rule) for rule in tool.selected_rules())
        # Another situation where we add default rules is when there are no rules
        # selected yet (and we haven't explicitly been requested to add minimal config).
        or not tool.selected_rules()
    ):
        rule_config = _get_basic_rule_config()
        for _tool in ALL_TOOLS:
            if not _tool.rule_config.empty and _tool.is_used():
                rule_config |= _tool.rule_config
    else:
        rule_config = RuleConfig()

    if not remove:
        tool = RuffTool(
            linter_detection="always" if linter else "auto",
            formatter_detection="always" if formatter else "auto",
        )

        ensure_dep_declaration_file()

        tool.add_dev_deps()
        tool.add_configs()

        if linter:
            tool.apply_rule_config(rule_config)
        tool.add_pre_commit_config()

        tool.print_how_to_use()
    else:
        tool = RuffTool(
            linter_detection="never" if not linter else "always",
            formatter_detection="never" if not formatter else "always",
        )

        tool.remove_pre_commit_repo_configs()
        tool.remove_configs()
        tool.remove_dev_deps()
        tool.remove_managed_files()


def _get_basic_rule_config() -> RuleConfig:
    """Get the basic rule config for Ruff."""
    # This is not merged with existing config; it's a sensible default set of rules if
    # starting from nothing. See the `use_ruff()` docstring.

    rule_config = RuleConfig(
        selected=[
            "A",
            "C4",
            "E4",
            "E7",
            "E9",
            "F",
            "FLY",
            "FURB",
            "I",
            "PLE",
            "PLR",
            "RUF",
            "SIM",
            "UP",
        ],
        ignored=[
            "PLR2004",  # https://github.com/usethis-python/usethis-python/issues/105
            "SIM108",  # https://github.com/usethis-python/usethis-python/issues/118
        ],
        tests_ignored=[
            "RUF059",  # https://github.com/usethis-python/usethis-python/issues/1186
        ],
    )

    return rule_config


def use_ty(*, remove: bool = False, how: bool = False) -> None:
    """Add or remove ty from the project."""
    tool = TyTool()

    if how:
        tool.print_how_to_use()
        return

    if not remove:
        ensure_dep_declaration_file()

        tool.add_dev_deps()
        tool.add_pre_commit_config()

        tool.add_configs()
        tool.print_how_to_use()
    else:
        tool.remove_configs()
        tool.remove_pre_commit_repo_configs()
        tool.remove_dev_deps()
        tool.remove_managed_files()


def use_tool(  # noqa: PLR0912
    tool: SupportedToolType,
    *,
    remove: bool = False,
    how: bool = False,
) -> None:
    """General dispatch function to add or remove a tool to/from the project.

    This is mostly intended for situations when the exact tool being added is not known
    dynamically. If you know the specific tool you wish to add, it is strongly
    recommended to call the specific function directly, e.g. `use_codespell()`, etc.
    """
    # One might wonder why we don't just implement a `use` method on the Tool class
    # itself. Basically it's for architectural reasons: we want to keep a layer of
    # abstraction between the tool and the logic to actually configure it.
    # In the future, that might change if we can create a sufficiently generalized logic
    # for all tools such that bespoke choices on a per-tool basis are not required, and
    # all the logic is just deterministic based on the tool's properties/methods, etc.
    if isinstance(tool, CodespellTool):
        use_codespell(remove=remove, how=how)
    elif isinstance(tool, CoveragePyTool):
        use_coverage_py(remove=remove, how=how)
    elif isinstance(tool, DeptryTool):
        use_deptry(remove=remove, how=how)
    elif isinstance(tool, ImportLinterTool):
        use_import_linter(remove=remove, how=how)
    elif isinstance(tool, MkDocsTool):
        use_mkdocs(remove=remove, how=how)
    elif isinstance(tool, PreCommitTool):
        use_pre_commit(remove=remove, how=how)
    elif isinstance(tool, PyprojectFmtTool):
        use_pyproject_fmt(remove=remove, how=how)
    elif isinstance(tool, PyprojectTOMLTool):
        use_pyproject_toml(remove=remove, how=how)
    elif isinstance(tool, PytestTool):
        use_pytest(remove=remove, how=how)
    elif isinstance(tool, RequirementsTxtTool):
        use_requirements_txt(remove=remove, how=how)
    elif isinstance(tool, RuffTool):
        use_ruff(remove=remove, how=how)
    elif isinstance(tool, TyTool):
        use_ty(remove=remove, how=how)
    else:
        # Having the assert_never here is effectively a way of testing cases are
        # exhaustively handled, which ensures it is kept up to date with ALL_TOOLS,
        # together with the type annotation on ALL_TOOLS itself. That's why this
        # function is implemented as a series of `if` statements rather than a
        # dictionary or similar alternative.
        assert_never(tool)
