import sys

import typer

from usethis._config import offline_opt, quiet_opt, usethis_config
from usethis._console import box_print, err_print
from usethis._integrations.pre_commit.core import (
    add_pre_commit_config,
    install_pre_commit,
    remove_pre_commit_config,
    uninstall_pre_commit,
)
from usethis._integrations.pytest.core import add_pytest_dir, remove_pytest_dir
from usethis._integrations.ruff.rules import deselect_ruff_rules, select_ruff_rules
from usethis._integrations.uv.deps import add_deps_to_group, remove_deps_from_group
from usethis._tool import (
    ALL_TOOLS,
    DeptryTool,
    PreCommitTool,
    PyprojectFmtTool,
    PytestTool,
    RuffTool,
)
from usethis.errors import UsethisError

app = typer.Typer(help="Add and configure development tools, e.g. linters.")


@app.command(
    help="Use the deptry linter: avoid missing or superfluous dependency declarations."
)
def deptry(
    remove: bool = typer.Option(
        False, "--remove", help="Remove deptry instead of adding it."
    ),
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
) -> None:
    try:
        with usethis_config.set(offline=offline, quiet=quiet):
            _deptry(remove=remove)
    except UsethisError as err:
        err_print(err)
        sys.exit(1)


def _deptry(*, remove: bool = False) -> None:
    tool = DeptryTool()

    if not remove:
        add_deps_to_group(tool.dev_deps, "dev")
        if PreCommitTool().is_used():
            tool.add_pre_commit_repo_config()

        box_print("Call the 'deptry src' command to run deptry.")
    else:
        if PreCommitTool().is_used():
            tool.remove_pre_commit_repo_config()
        remove_deps_from_group(tool.dev_deps, "dev")


@app.command(
    help="Use the pre-commit framework to manage and maintain pre-commit hooks."
)
def pre_commit(
    remove: bool = typer.Option(
        False, "--remove", help="Remove pre-commit instead of adding it."
    ),
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
) -> None:
    try:
        with usethis_config.set(offline=offline, quiet=quiet):
            _pre_commit(remove=remove)
    except UsethisError as err:
        err_print(err)
        sys.exit(1)


def _pre_commit(*, remove: bool = False) -> None:
    tool = PreCommitTool()

    if not remove:
        add_deps_to_group(tool.dev_deps, "dev")
        add_pre_commit_config()
        for _tool in ALL_TOOLS:
            if _tool.is_used():
                _tool.add_pre_commit_repo_config()
        install_pre_commit()

        box_print(
            "Call the 'pre-commit run --all-files' command to run the hooks manually."
        )
    else:
        # Need pre-commit to be installed so we can uninstall hooks
        add_deps_to_group(tool.dev_deps, "dev")

        uninstall_pre_commit()
        remove_pre_commit_config()
        remove_deps_from_group(tool.dev_deps, "dev")

        # Need to add a new way of running some hooks manually if they are not dev
        # dependencies yet
        if PyprojectFmtTool().is_used():
            _pyproject_fmt()


@app.command(
    help="Use the pyproject-fmt linter: opinionated formatting of 'pyproject.toml' files."
)
def pyproject_fmt(
    remove: bool = typer.Option(
        False, "--remove", help="Remove pyproject-fmt instead of adding it."
    ),
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
) -> None:
    try:
        with usethis_config.set(offline=offline, quiet=quiet):
            _pyproject_fmt(remove=remove)
    except UsethisError as err:
        err_print(err)
        sys.exit(1)


def _pyproject_fmt(*, remove: bool = False) -> None:
    tool = PyprojectFmtTool()

    if not remove:
        is_precommit = PreCommitTool().is_used()

        if not is_precommit:
            add_deps_to_group(tool.dev_deps, "dev")
        else:
            tool.add_pre_commit_repo_config()

        tool.add_pyproject_configs()

        if not is_precommit:
            box_print(
                "Call the 'pyproject-fmt pyproject.toml' command to run pyproject-fmt."
            )
        else:
            box_print(
                "Call the 'pre-commit run pyproject-fmt --all-files' command to run pyproject-fmt."
            )
    else:
        tool.remove_pyproject_configs()
        if PreCommitTool().is_used():
            tool.remove_pre_commit_repo_config()
        remove_deps_from_group(tool.dev_deps, "dev")


@app.command(help="Use the pytest testing framework.")
def pytest(
    remove: bool = typer.Option(
        False, "--remove", help="Remove pytest instead of adding it."
    ),
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
) -> None:
    try:
        with usethis_config.set(offline=offline, quiet=quiet):
            _pytest(remove=remove)
    except UsethisError as err:
        err_print(err)
        sys.exit(1)


def _pytest(*, remove: bool = False) -> None:
    tool = PytestTool()

    if not remove:
        add_deps_to_group(tool.dev_deps, "test")
        tool.add_pyproject_configs()
        if RuffTool().is_used():
            select_ruff_rules(tool.get_associated_ruff_rules())
        # deptry currently can't scan the tests folder for dev deps
        # https://github.com/fpgmaas/deptry/issues/302
        add_pytest_dir()

        box_print(
            "Add test files to the '/tests' directory with the format 'test_*.py'."
        )
        box_print("Add test functions with the format 'test_*()'.")
        box_print("Call the 'pytest' command to run the tests.")
    else:
        if RuffTool().is_used():
            deselect_ruff_rules(tool.get_associated_ruff_rules())
        tool.remove_pyproject_configs()
        remove_deps_from_group(tool.dev_deps, "test")
        remove_pytest_dir()  # Last, since this is a manual step


@app.command(help="Use ruff: an extremely fast Python linter and code formatter.")
def ruff(
    remove: bool = typer.Option(
        False, "--remove", help="Remove ruff instead of adding it."
    ),
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
) -> None:
    try:
        with usethis_config.set(offline=offline, quiet=quiet):
            _ruff(remove=remove)
    except UsethisError as err:
        err_print(err)
        sys.exit(1)


def _ruff(*, remove: bool = False) -> None:
    tool = RuffTool()

    rules = [
        "C4",
        "E4",
        "E7",
        "E9",
        "F",
        "FURB",
        "I",
        "PLE",
        "PLR",
        "RUF",
        "SIM",
        "UP",
    ]
    for _tool in ALL_TOOLS:
        if _tool.is_used():
            rules += _tool.get_associated_ruff_rules()

    if not remove:
        add_deps_to_group(tool.dev_deps, "dev")
        tool.add_pyproject_configs()
        select_ruff_rules(rules)
        if PreCommitTool().is_used():
            tool.add_pre_commit_repo_config()

        box_print(
            "Call the 'ruff check --fix' command to run the ruff linter with autofixes."
        )
        box_print("Call the 'ruff format' command to run the ruff formatter.")
    else:
        if PreCommitTool().is_used():
            tool.remove_pre_commit_repo_config()
        tool.remove_pyproject_configs()  # N.B. this will remove the selected ruff rules
        remove_deps_from_group(tool.dev_deps, "dev")
