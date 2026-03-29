"""Testing toolset."""

from usethis._core.tool import use_coverage_py, use_pytest


def use_test_frameworks(remove: bool = False, how: bool = False):
    """Add and configure testing framework tools for the project."""
    use_pytest(remove=remove, how=how)
    use_coverage_py(remove=remove, how=how)
