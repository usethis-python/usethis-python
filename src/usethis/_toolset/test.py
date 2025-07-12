from usethis._core.tool import use_coverage_py, use_pytest


def use_test_frameworks(remove: bool = False, how: bool = False):
    use_pytest(remove=remove, how=how)
    use_coverage_py(remove=remove, how=how)
