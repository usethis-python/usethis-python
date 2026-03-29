"""Type checking toolset."""

from usethis._core.tool import use_ty


def use_typecheckers(remove: bool = False, how: bool = False):
    """Add or remove type checking tools."""
    use_ty(remove=remove, how=how)
