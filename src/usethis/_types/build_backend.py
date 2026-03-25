from enum import Enum


class BuildBackendEnum(Enum):
    """Enumeration of available build backends for project initialization.

    These correspond to a subset of the build backends supported by
    `uv init --build-backend`.
    """

    hatch = "hatch"
    uv = "uv"
