"""Documentation toolset."""

from usethis._core.tool import use_mkdocs


def use_doc_frameworks(remove: bool = False, how: bool = False):
    """Add or remove documentation framework tools."""
    use_mkdocs(remove=remove, how=how)
