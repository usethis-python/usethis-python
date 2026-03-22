from enum import Enum


class BuildBackendEnum(Enum):
    """Enumeration of available build backends for project initialization.

    These correspond to the build backends supported by `uv init --build-backend`.
    """

    hatch = "hatch"
    uv = "uv"
    flit = "flit"
    pdm = "pdm"
    setuptools = "setuptools"
    maturin = "maturin"
    scikit = "scikit"
    poetry = "poetry"
