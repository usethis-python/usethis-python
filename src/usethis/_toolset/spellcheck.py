from usethis._core.tool import use_codespell


def use_spellcheckers(remove: bool = False, how: bool = False):
    use_codespell(remove=remove, how=how)
