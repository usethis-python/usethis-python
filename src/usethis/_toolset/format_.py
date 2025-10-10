from usethis._core.tool import use_pyproject_fmt, use_ruff
from usethis._tool.impl.pyproject_toml import PyprojectTOMLTool


def use_formatters(remove: bool = False, how: bool = False):
    use_ruff(linter=False, formatter=True, remove=remove, how=how)
    if PyprojectTOMLTool().is_used() and (not remove or how):
        use_pyproject_fmt(remove=remove, how=how)
