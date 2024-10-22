from packaging.requirements import Requirement
from pydantic import TypeAdapter

from usethis._pyproject.io import read_pyproject_toml


def get_dev_deps() -> list[str]:
    pyproject = read_pyproject_toml()
    try:
        dev_deps_section = pyproject["tool"]["uv"]["dev-dependencies"]
    except KeyError:
        return []

    req_strs = TypeAdapter(list[str]).validate_python(dev_deps_section)
    reqs = [Requirement(req_str) for req_str in req_strs]
    return [req.name for req in reqs]
