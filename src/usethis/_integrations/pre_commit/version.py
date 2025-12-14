from usethis._config import usethis_config
from usethis._integrations.pre_commit.io_ import read_pre_commit_config_yaml


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
