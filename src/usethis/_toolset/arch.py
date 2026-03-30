"""Architecture enforcement toolset."""

from usethis._core.tool import use_import_linter, use_tach


def use_arch_tools(remove: bool = False, how: bool = False):
    """Add and configure architecture enforcement tools for the project."""
    use_import_linter(remove=remove, how=how)
    use_tach(remove=remove, how=how)
