from usethis._config import usethis_config
from usethis._console import tick_print
from usethis._integrations.project.name import get_project_name


def add_docs_dir() -> None:
    """Create the `docs` directory and an `docs/index.md` file if they do not exist."""
    docs_dir = usethis_config.cpd() / "docs"
    if not docs_dir.exists():
        tick_print("Creating '/docs'.")
        docs_dir.mkdir()
        write_index = True
    elif not (docs_dir / "index.md").exists():
        tick_print("Writing '/docs/index.md'.")
        write_index = True
    else:
        write_index = False
    if write_index:
        (docs_dir / "index.md").write_text(
            f"""\
# {get_project_name()}

Welcome to the documentation for {get_project_name()}.
"""
        )
