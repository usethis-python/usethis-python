from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, InstanceOf

from usethis._io import UsethisFileManager


class ConfigSpec(BaseModel):
    """Specification of configuration files for a tool.

    Attributes:
        file_managers: List of file managers that handle the configuration files.
        resolution: The resolution strategy for the configuration files.
                    - "first": Using the order in file_managers, the first file found to
                      exist is used. All subsequent files are ignored. If no files are
                      found, the first file in the list is used.
    """

    file_managers: list[InstanceOf[UsethisFileManager]]
    resolution: Literal["first"]
