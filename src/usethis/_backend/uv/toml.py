"""Manager for the uv.toml configuration file."""

from pathlib import Path

from typing_extensions import override

from usethis._file.toml.io_ import TOMLFileManager


class UVTOMLManager(TOMLFileManager):
    """Class to manage the uv.toml file."""

    @property
    @override
    def relative_path(self) -> Path:
        return Path("uv.toml")
