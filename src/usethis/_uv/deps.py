from pathlib import Path

import tomlkit
from packaging.requirements import Requirement
from pydantic import TypeAdapter


def get_dev_deps(proj_dir: Path) -> list[str]:
    pyproject = tomlkit.parse((proj_dir / "pyproject.toml").read_text())
    try:
        dev_deps_section = pyproject["tool"]["uv"]["dev-dependencies"]
    except KeyError:
        return []

    req_strs = TypeAdapter(list[str]).validate_python(dev_deps_section)
    reqs = [Requirement(req_str) for req_str in req_strs]
    return [req.name for req in reqs]
