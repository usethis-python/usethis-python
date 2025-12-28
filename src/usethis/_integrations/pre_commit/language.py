from packaging.version import Version

from usethis._integrations.pre_commit.schema import Language
from usethis._integrations.pre_commit.version import get_minimum_pre_commit_version


def get_system_language() -> Language:
    """Get the appropriate 'system' language keyword based on pre-commit version.

    Returns 'unsupported' for pre-commit >= 4.4.0, otherwise 'system'.

    In the future, there may be a deprecation of the 'system' language in pre-commit,
    at which point falling back to 'system' may no longer be appropriate and this logic
    will need to be revisited.
    """
    min_version = get_minimum_pre_commit_version()
    if min_version is not None and Version(min_version) >= Version("4.4.0"):
        return Language("unsupported")
    return Language("system")
