import re
import subprocess

from packaging.requirements import Requirement
from pydantic import TypeAdapter

from usethis._console import console
from usethis._integrations.pyproject.io import read_pyproject_toml


def get_dev_deps() -> list[str]:
    pyproject = read_pyproject_toml()
    try:
        dev_deps_section = pyproject["tool"]["uv"]["dev-dependencies"]
    except KeyError:
        return []

    req_strs = TypeAdapter(list[str]).validate_python(dev_deps_section)
    reqs = [Requirement(req_str) for req_str in req_strs]
    return [req.name for req in reqs]


def add_dev_deps(pypi_names: list[str], *, offline: bool) -> None:
    """Add a package as a development dependency, if not already added."""
    existing_dev_deps = get_dev_deps()

    for dep in pypi_names:
        if _strip_extras(dep) in existing_dev_deps:
            # Early exit; the tool is already a dev dependency.
            continue

        console.print(f"✔ Adding '{dep}' as a development dependency.", style="green")
        if not offline:
            subprocess.run(
                ["uv", "add", "--dev", "--quiet", dep],
                check=True,
            )
        else:
            subprocess.run(
                ["uv", "add", "--dev", "--quiet", "--offline", dep],
                check=True,
            )


def remove_dev_deps(pypi_names: list[str], *, offline: bool) -> None:
    """Remove the tool's development dependencies, if present."""
    existing_dev_deps = get_dev_deps()

    for dep in pypi_names:
        if _strip_extras(dep) not in existing_dev_deps:
            # Early exit; the tool is already not a dev dependency.
            continue

        console.print(
            f"✔ Removing '{dep}' as a development dependency.",
            style="green",
        )
        if not offline:
            subprocess.run(
                ["uv", "remove", "--dev", "--quiet", _strip_extras(dep)], check=True
            )
        else:
            subprocess.run(
                ["uv", "remove", "--dev", "--quiet", "--offline", _strip_extras(dep)],
                check=True,
            )


def is_dep_used(dep: str) -> bool:
    return _strip_extras(dep) in get_dev_deps()


def _strip_extras(dep: str) -> str:
    """Remove extras from a dependency string."""
    return re.sub(r"\[.*\]", "", dep)
