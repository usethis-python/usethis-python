from usethis._core.tool import use_pyproject_fmt, use_ruff


def use_formatters(remove: bool = False, how: bool = False):
    use_ruff(linter=False, formatter=True, remove=remove, how=how)
    use_pyproject_fmt(remove=remove, how=how)
