from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Literal, final

from typing_extensions import override

from usethis._config import usethis_config
from usethis._config_file import DotRuffTOMLManager, RuffTOMLManager
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._tool.base import ToolMeta, ToolSpec
from usethis._tool.config import ConfigEntry, ConfigItem, ConfigSpec
from usethis._types.deps import Dependency

if TYPE_CHECKING:
    from usethis._io import KeyValueFileManager


class RuffToolSpec(ToolSpec):
    linter_detection: Literal["auto", "always", "never"]
    formatter_detection: Literal["auto", "always", "never"]
    is_auto_detection: bool

    @final
    def __init__(
        self,
        linter_detection: Literal["auto", "always", "never"] = "auto",
        formatter_detection: Literal["auto", "always", "never"] = "auto",
    ):
        """Initialize the Ruff management class.

        Args:
            linter_detection: A method to determine whether the linter is being used. By
                              default, it will be determined using heuristics
                              automatically, but this can be over-ridden.
            formatter_detection: A method to determine whether the formatter is used. By
                                 default, it will be determined using heuristics
                                 automatically, but this can be over-ridden.
        """
        self.linter_detection = linter_detection
        self.formatter_detection = formatter_detection
        self.is_auto_detection = (linter_detection == "auto") and (
            formatter_detection == "auto"
        )

    @final
    @property
    @override
    def meta(self) -> ToolMeta:
        return ToolMeta(
            name="Ruff",
            url="https://github.com/astral-sh/ruff",
            managed_files=[Path(".ruff.toml"), Path("ruff.toml")],
        )

    @override
    @final
    def dev_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        return [Dependency(name="ruff")]

    @override
    @final
    def preferred_file_manager(self) -> KeyValueFileManager[object]:
        if (usethis_config.cpd() / "pyproject.toml").exists():
            return PyprojectTOMLManager()
        return RuffTOMLManager()

    @override
    @final
    def config_spec(self) -> ConfigSpec:
        # https://docs.astral.sh/ruff/configuration/#config-file-discovery

        line_length = 88

        config_items = [
            ConfigItem(
                description="Overall config",
                root={
                    Path(".ruff.toml"): ConfigEntry(keys=[]),
                    Path("ruff.toml"): ConfigEntry(keys=[]),
                    Path("pyproject.toml"): ConfigEntry(keys=["tool", "ruff"]),
                },
                # If the detection method is "never" for either the linter or formatter,
                # then we shouldn't remove the overall config section. And when it comes
                # to adding, it will be added regardless since there are other config
                # subsections below.
                managed=not (
                    (self.linter_detection == "never")
                    or (self.formatter_detection == "never")
                ),
            ),
        ]
        if self.linter_detection == "always":
            config_items.extend(
                [
                    ConfigItem(
                        description="Linter config",
                        root={
                            Path(".ruff.toml"): ConfigEntry(keys=["lint"]),
                            Path("ruff.toml"): ConfigEntry(keys=["lint"]),
                            Path("pyproject.toml"): ConfigEntry(
                                keys=["tool", "ruff", "lint"]
                            ),
                        },
                    ),
                    ConfigItem(
                        description="Line length",
                        root={
                            Path(".ruff.toml"): ConfigEntry(
                                keys=["line-length"], get_value=lambda: line_length
                            ),
                            Path("ruff.toml"): ConfigEntry(
                                keys=["line-length"], get_value=lambda: line_length
                            ),
                            Path("pyproject.toml"): ConfigEntry(
                                keys=["tool", "ruff", "line-length"],
                                get_value=lambda: line_length,
                            ),
                        },
                    ),
                ]
            )
        if self.formatter_detection == "always":
            config_items.extend(
                [
                    ConfigItem(
                        description="Formatter config",
                        root={
                            Path(".ruff.toml"): ConfigEntry(keys=["format"]),
                            Path("ruff.toml"): ConfigEntry(keys=["format"]),
                            Path("pyproject.toml"): ConfigEntry(
                                keys=["tool", "ruff", "format"]
                            ),
                        },
                    ),
                    ConfigItem(
                        description="Docstring Code Format",
                        root={
                            Path(".ruff.toml"): ConfigEntry(
                                keys=["format", "docstring-code-format"],
                                get_value=lambda: True,
                            ),
                            Path("ruff.toml"): ConfigEntry(
                                keys=["format", "docstring-code-format"],
                                get_value=lambda: True,
                            ),
                            Path("pyproject.toml"): ConfigEntry(
                                keys=[
                                    "tool",
                                    "ruff",
                                    "format",
                                    "docstring-code-format",
                                ],
                                get_value=lambda: True,
                            ),
                        },
                    ),
                ]
            )

        return ConfigSpec.from_flat(
            file_managers=[
                DotRuffTOMLManager(),
                RuffTOMLManager(),
                PyprojectTOMLManager(),
            ],
            resolution="first",
            config_items=config_items,
        )
