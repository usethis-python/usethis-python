"""Type checking toolset."""

from usethis._core.tool import use_ty


def use_typecheckers(remove: bool = False, how: bool = False):
    """Add and configure type checking tools for the project."""
    use_ty(remove=remove, how=how)
