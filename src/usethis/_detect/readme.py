from usethis._integrations.readme.path import get_readme_path


def is_readme_used():
    """Check if the README.md file is used."""
    try:
        _ = get_readme_path()
    except FileNotFoundError:
        return False

    return True
