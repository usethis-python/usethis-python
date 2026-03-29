"""Spell checking toolset."""

from usethis._core.tool import use_codespell


def use_spellcheckers(remove: bool = False, how: bool = False):
    """Add or remove spell checking tools."""
    use_codespell(remove=remove, how=how)
