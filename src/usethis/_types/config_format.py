from enum import Enum


class ConfigFormatEnum(Enum):
    """Enumeration of available configuration file formats."""

    toml = "toml"
    ini = "ini"
