from __future__ import annotations

from pathlib import Path

import typer
from typing_extensions import assert_never

from usethis._config import usethis_config
from usethis._types.backend import BackendEnum
from usethis._types.ci import CIServiceEnum
from usethis._types.docstyle import DocStyleEnum
from usethis._types.status import DevelopmentStatusEnum
from usethis._ui.options import (
    backend_opt,
    frozen_opt,
    init_arch_opt,
    init_ci_opt,
    init_doc_opt,
    init_docstyle_opt,
    init_format_opt,
    init_hook_opt,
    init_lint_opt,
    init_path_arg,
    init_spellcheck_opt,
    init_status_opt,
    init_test_opt,
    init_typecheck_opt,
    offline_opt,
    quiet_opt,
)


def init(
    arch: bool = init_arch_opt,
    doc: bool = init_doc_opt,
    format_: bool = init_format_opt,
    lint: bool = init_lint_opt,
    spellcheck: bool = init_spellcheck_opt,
    test: bool = init_test_opt,
    typecheck: bool = init_typecheck_opt,
    hook: bool = init_hook_opt,
    ci: CIServiceEnum | None = init_ci_opt,
    docstyle: DocStyleEnum | None = init_docstyle_opt,
    status: DevelopmentStatusEnum = init_status_opt,
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
    frozen: bool = frozen_opt,
    backend: BackendEnum = backend_opt,
    path: str | None = init_path_arg,
) -> None:
    """Initialize a new project with recommended tooling."""
    from usethis._config_file import files_manager
    from usethis._console import err_print, instruct_print
    from usethis.errors import UsethisError

    assert isinstance(backend, BackendEnum)

    if path is not None:
        path_ = Path(path)
        if not path_.exists():
            path_.mkdir(parents=True, exist_ok=True)

        instruct_print("Change the current working directory to the project directory.")

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
                arch=arch,
                doc=doc,
                format_=format_,
                lint=lint,
                spellcheck=spellcheck,
                test=test,
                typecheck=typecheck,
                hook=hook,
                ci=ci,
                docstyle=docstyle,
                status=status,
            )
        except UsethisError as err:
            err_print(err)
            raise typer.Exit(code=1) from None


def _init(  # noqa: PLR0915
    *,
    arch: bool,
    doc: bool,
    format_: bool,
    lint: bool,
    spellcheck: bool,
    test: bool,
    typecheck: bool,
    hook: bool,
    ci: CIServiceEnum | None,
    docstyle: DocStyleEnum | None,
    status: DevelopmentStatusEnum,
):
    from usethis._console import tick_print
    from usethis._core.ci import print_how_to_use_ci_bitbucket, use_ci_bitbucket
    from usethis._core.docstyle import use_docstyle
    from usethis._core.readme import add_readme
    from usethis._core.status import use_development_status
    from usethis._init import project_init
    from usethis._toolset.arch import use_arch_tools
    from usethis._toolset.doc import use_doc_frameworks
    from usethis._toolset.format_ import use_formatters
    from usethis._toolset.hook import use_hook_framework
    from usethis._toolset.lint import use_linters
    from usethis._toolset.spellcheck import use_spellcheckers
    from usethis._toolset.test import use_test_frameworks
    from usethis._toolset.typecheck import use_typecheckers

    project_init()
    add_readme()

    assert isinstance(status, DevelopmentStatusEnum)
    use_development_status(status)

    if hook:
        tick_print("Adding a recommended git hook framework.")
        with usethis_config.set(instruct_only=True):
            use_hook_framework()
        use_hook_framework(how=True)

    if doc:
        tick_print("Adding recommended documentation tools.")
        with usethis_config.set(instruct_only=True):
            use_doc_frameworks()
        use_doc_frameworks(how=True)
    if lint:
        tick_print("Adding recommended linters.")
        with usethis_config.set(instruct_only=True):
            use_linters()
        use_linters(how=True)
    if format_:
        tick_print("Adding recommended formatters.")
        with usethis_config.set(instruct_only=True):
            use_formatters()
        use_formatters(how=True)
    if docstyle is not None:
        tick_print(f"Setting docstring style to {docstyle.value}.")
        assert isinstance(docstyle, DocStyleEnum)
        with usethis_config.set(instruct_only=True):
            use_docstyle(style=docstyle)
    if spellcheck:
        tick_print("Adding recommended spellcheckers.")
        with usethis_config.set(instruct_only=True):
            use_spellcheckers()
        use_spellcheckers(how=True)
    if test:
        tick_print("Adding recommended test frameworks.")
        with usethis_config.set(instruct_only=True):
            use_test_frameworks()
        use_test_frameworks(how=True)
    if typecheck:
        tick_print("Adding recommended type checkers.")
        with usethis_config.set(instruct_only=True):
            use_typecheckers()
        use_typecheckers(how=True)
    if arch:
        tick_print("Adding recommended architecture analysis tools.")
        with usethis_config.set(instruct_only=True):
            use_arch_tools()
        use_arch_tools(how=True)

    if ci is not None:
        assert isinstance(ci, CIServiceEnum)
        if ci is CIServiceEnum.bitbucket:
            tick_print("Adding Bitbucket Pipelines configuration.")
            with usethis_config.set(instruct_only=True):
                use_ci_bitbucket()
            print_how_to_use_ci_bitbucket()
        else:
            assert_never(ci)
