from __future__ import annotations

from usethis._config import usethis_config
from usethis._deps import is_dep_in_any_group
from usethis._types.deps import Dependency


def is_pre_commit_used() -> bool:
    """Check if pre-commit is being used in the project.

    Returns True if either:
    1. The .pre-commit-config.yaml file exists, or
    2. pre-commit is declared as a dependency
    """
    if usethis_config.disable_pre_commit:
        return False

    if (usethis_config.cpd() / ".pre-commit-config.yaml").exists():
        return True

    return is_dep_in_any_group(Dependency(name="pre-commit"))
