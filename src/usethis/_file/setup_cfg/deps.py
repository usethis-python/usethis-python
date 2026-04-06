"""Dependency extraction from setup.cfg."""

from __future__ import annotations

from packaging.requirements import Requirement

from usethis._file.setup_cfg.io_ import SetupCFGManager
from usethis._types.deps import Dependency


def get_setup_cfg_project_deps() -> list[Dependency]:
    """Get project dependencies from setup.cfg [options] install_requires.

    This reads the ``install_requires`` field from the ``[options]`` section of
    ``setup.cfg``, which is the legacy setuptools way of declaring project dependencies.
    """
    try:
        cfg = SetupCFGManager().get()
    except FileNotFoundError:
        return []

    if "options" not in cfg:
        return []

    if "install_requires" not in cfg["options"]:
        return []

    raw_value = cfg["options"]["install_requires"].value
    return _parse_deps_string(raw_value or "")


def get_setup_cfg_dep_groups() -> dict[str, list[Dependency]]:
    """Get dependency groups from setup.cfg [options.extras_require].

    This reads the ``[options.extras_require]`` section of ``setup.cfg``, which is the
    legacy setuptools way of declaring optional/extra dependencies. Each extra is treated
    as a dependency group.
    """
    try:
        cfg = SetupCFGManager().get()
    except FileNotFoundError:
        return {}

    if "options.extras_require" not in cfg:
        return {}

    result: dict[str, list[Dependency]] = {}
    for extra_name in cfg["options.extras_require"].options():
        raw_value = cfg["options.extras_require"][extra_name].value
        deps = _parse_deps_string(raw_value or "")
        if deps:
            result[extra_name] = deps

    return result


def _parse_deps_string(raw_value: str) -> list[Dependency]:
    """Parse a multiline dependency string from setup.cfg into a list of Dependency objects.

    Each non-empty, non-comment line is treated as a PEP 508 requirement string.
    """
    result: list[Dependency] = []
    for line in raw_value.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        req = Requirement(line)
        result.append(Dependency(name=req.name, extras=frozenset(req.extras)))
    return result
