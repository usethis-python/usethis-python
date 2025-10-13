from usethis._core.tool import use_deptry, use_ruff


def use_linters(remove: bool = False, how: bool = False):
    # Use deptry first since it determines that we use 'pyproject.toml' for Ruff.
    use_deptry(remove=remove, how=how)
    use_ruff(linter=True, formatter=False, remove=remove, how=how)
