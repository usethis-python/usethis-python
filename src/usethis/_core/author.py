# TODO can we default to git info?
# TODO neither name or email is strictly required, but at least one is.


from usethis._integrations.file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._integrations.uv.init import ensure_pyproject_toml


def add_author(
    *,
    name: str,
    email: str,
):
    ensure_pyproject_toml(author=False)

    PyprojectTOMLManager().extend_list(
        keys=["project", "authors"],
        values=[{"name": name, "email": email}],
    )
