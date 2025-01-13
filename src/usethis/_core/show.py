from usethis._integrations.pyproject.name import get_name
from usethis._integrations.uv.init import ensure_pyproject_toml


def show_name() -> None:
    ensure_pyproject_toml()
    print(get_name())
