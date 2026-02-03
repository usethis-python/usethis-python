from pathlib import Path

from usethis._file.toml.io_ import TOMLFileManager


class UVTOMLManager(TOMLFileManager):
    """Class to manage the uv.toml file."""

    @property
    def relative_path(self) -> Path:
        return Path("uv.toml")
