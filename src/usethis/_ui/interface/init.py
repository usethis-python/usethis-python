from __future__ import annotations

from pathlib import Path

import typer

from usethis._types.backend import BackendEnum
from usethis._types.ci import CIServiceEnum
from usethis._types.docstyle import DocStyleEnum
from usethis._types.status import DevelopmentStatusEnum
from usethis._ui.options import backend_opt, frozen_opt, offline_opt, quiet_opt


def init(  # noqa: PLR0913
    doc: bool = typer.Option(
        True, "--doc/--no-doc", help="Add a recommended documentation framework."
    ),
    format_: bool = typer.Option(
        True, "--format/--no-format", help="Add recommended formatters."
    ),
    lint: bool = typer.Option(
        True, "--lint/--no-lint", help="Add recommended linters."
    ),
    spellcheck: bool = typer.Option(
        True,
        "--spellcheck/--no-spellcheck",
        help="Add a recommended spellchecker.",
    ),
    test: bool = typer.Option(
        True,
        "--test/--no-test",
        help="Add a recommended testing framework.",
    ),
    pre_commit: bool = typer.Option(
        False,
        "--pre-commit/--no-pre-commit",
        help="Add the pre-commit framework for git hooks.",
    ),
    ci: CIServiceEnum | None = typer.Option(
        None,
        "--ci",
        help="Add a CI service configuration.",
    ),
    docstyle: DocStyleEnum | None = typer.Option(
        None,
        "--docstyle",
        help="Set a docstring style convention for the project.",
    ),
    status: DevelopmentStatusEnum = typer.Option(
        "planning",
        "--status",
        help="Set the development status of the project.",
    ),
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
    frozen: bool = frozen_opt,
    backend: BackendEnum = backend_opt,
    path: str | None = typer.Argument(
        None,
        help="The path to use for the project. Defaults to the current working directory.",
    ),
) -> None:
    """Initialize a new project with recommended tooling."""
    from usethis._config import usethis_config
    from usethis._config_file import files_manager
    from usethis._console import box_print, err_print
    from usethis.errors import UsethisError

    assert isinstance(backend, BackendEnum)

    if path is not None:
        box_print("Change the current working directory to the project directory.")

    if path is not None:
        path_ = Path(path)
        if not path_.exists():
            path_.mkdir(parents=True, exist_ok=True)

    with (
        usethis_config.set(
            offline=offline,
            quiet=quiet,
            frozen=frozen,
            backend=backend,
            project_dir=path,
        ),
        files_manager(),
    ):
        try:
            _init(
                doc=doc,
                format_=format_,
                lint=lint,
                spellcheck=spellcheck,
                test=test,
                pre_commit=pre_commit,
                ci=ci,
                docstyle=docstyle,
                status=status,
            )
        except UsethisError as err:
            err_print(err)
            raise typer.Exit(code=1) from None


def _init(  # noqa: PLR0913, PLR0915
    *,
    doc: bool,
    format_: bool,
    lint: bool,
    spellcheck: bool,
    test: bool,
    pre_commit: bool,
    ci: CIServiceEnum | None,
    docstyle: DocStyleEnum | None,
    status: DevelopmentStatusEnum,
):
    from typing_extensions import assert_never

    from usethis._config import usethis_config
    from usethis._console import tick_print
    from usethis._core.ci import print_how_to_use_ci_bitbucket, use_ci_bitbucket
    from usethis._core.docstyle import use_docstyle
    from usethis._core.readme import add_readme
    from usethis._core.status import use_development_status
    from usethis._core.tool import use_pre_commit
    from usethis._init import project_init
    from usethis._toolset.doc import use_doc_frameworks
    from usethis._toolset.format_ import use_formatters
    from usethis._toolset.lint import use_linters
    from usethis._toolset.spellcheck import use_spellcheckers
    from usethis._toolset.test import use_test_frameworks

    project_init()
    add_readme()

    assert isinstance(status, DevelopmentStatusEnum)
    use_development_status(status)

    if pre_commit:
        tick_print("Adding the pre-commit framework.")
        with usethis_config.set(alert_only=True):
            use_pre_commit()
        use_pre_commit(how=True)

    if doc:
        tick_print("Adding recommended documentation tools.")
        with usethis_config.set(alert_only=True):
            use_doc_frameworks()
        use_doc_frameworks(how=True)
    if lint:
        tick_print("Adding recommended linters.")
        with usethis_config.set(alert_only=True):
            use_linters()
        use_linters(how=True)
    if format_:
        tick_print("Adding recommended formatters.")
        with usethis_config.set(alert_only=True):
            use_formatters()
        use_formatters(how=True)
    if docstyle is not None:
        tick_print(f"Setting docstring style to {docstyle.value}.")
        assert isinstance(docstyle, DocStyleEnum)
        with usethis_config.set(alert_only=True):
            use_docstyle(style=docstyle)
    if spellcheck:
        tick_print("Adding recommended spellcheckers.")
        with usethis_config.set(alert_only=True):
            use_spellcheckers()
        use_spellcheckers(how=True)
    if test:
        tick_print("Adding recommended test frameworks.")
        with usethis_config.set(alert_only=True):
            use_test_frameworks()
        use_test_frameworks(how=True)

    if ci is not None:
        assert isinstance(ci, CIServiceEnum)
        if ci is CIServiceEnum.bitbucket:
            tick_print("Adding Bitbucket Pipelines configuration.")
            with usethis_config.set(alert_only=True):
                use_ci_bitbucket()
            print_how_to_use_ci_bitbucket()
        else:
            assert_never(ci)
