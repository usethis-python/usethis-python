from usethis._config import usethis_config
from usethis._integrations.pre_commit.yaml import PreCommitConfigYAMLManager


def get_minimum_pre_commit_version() -> str | None:
    """Get the declared minimum supported pre-commit version from the configuration.

    This is in a dot-separated digit format e.g. `3.6.2`.

    Returns `None` if no minimum version is explicitly declared.
    """
    path = usethis_config.cpd() / ".pre-commit-config.yaml"

    if not path.exists():
        return None

    mgr = PreCommitConfigYAMLManager()
    model = mgr.model_validate()
    return model.minimum_pre_commit_version
