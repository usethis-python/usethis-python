"""Architecture enforcement toolset."""

from usethis._core.tool import use_import_linter


def use_arch_tools(remove: bool = False, how: bool = False):
    """Add or remove architecture enforcement tools."""
    use_import_linter(remove=remove, how=how)
