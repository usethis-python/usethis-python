from usethis._config import usethis_config
from usethis._integrations.pre_commit.io_ import read_pre_commit_config_yaml

PRE_COMMIT_VERSION = "4.5.1"


def get_pre_commit_version() -> str:
    """Get an inferred pre-commit version for usethis to target.

    If no version can be inferred, a hard-coded version is used, corresponding to a
    recent release (see `_PRE_COMMIT_VERSION`).
    """
    version = get_minimum_pre_commit_version()
    if version is not None:
        return version
    return PRE_COMMIT_VERSION


def get_minimum_pre_commit_version() -> str | None:
    """Get the declared minimum supported pre-commit version from the configuration.

    This is in a dot-separated digit format e.g. `3.6.2`.

    Returns `None` if no minimum version is explicitly declared.
    """
    path = usethis_config.cpd() / ".pre-commit-config.yaml"

    if not path.exists():
        return None

    with read_pre_commit_config_yaml() as doc:
        return doc.model.minimum_pre_commit_version
