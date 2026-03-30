"""Spell checking toolset."""

from usethis._core.tool import use_codespell


def use_spellcheckers(remove: bool = False, how: bool = False):
    """Add and configure spellchecking tools for the project."""
    use_codespell(remove=remove, how=how)
