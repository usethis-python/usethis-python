"""Documentation toolset."""

from usethis._core.tool import use_zensical


def use_doc_frameworks(remove: bool = False, how: bool = False):
    """Add and configure documentation framework tools for the project."""
    use_zensical(remove=remove, how=how)
