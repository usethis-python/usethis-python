"""Git hook framework toolset."""

from usethis._core.tool import use_pre_commit


def use_hook_framework(remove: bool = False, how: bool = False):
    use_pre_commit(remove=remove, how=how)
