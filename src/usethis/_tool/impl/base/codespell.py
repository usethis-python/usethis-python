from __future__ import annotations

from pathlib import Path

from usethis._config_file import DotCodespellRCManager
from usethis._console import how_print
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._file.setup_cfg.io_ import SetupCFGManager
from usethis._tool.base import Tool
from usethis._tool.config import ConfigEntry, ConfigItem, ConfigSpec
from usethis._tool.impl.spec.codespell import CodespellToolSpec


class CodespellTool(CodespellToolSpec, Tool):
    def config_spec(self) -> ConfigSpec:
        # https://github.com/codespell-project/codespell?tab=readme-ov-file#using-a-config-file

        return ConfigSpec.from_flat(
            file_managers=[
                DotCodespellRCManager(),
                SetupCFGManager(),
                PyprojectTOMLManager(),
            ],
            resolution="first_content",
            config_items=[
                ConfigItem(
                    description="Overall config",
                    root={
                        Path(".codespellrc"): ConfigEntry(keys=[]),
                        Path("setup.cfg"): ConfigEntry(keys=["codespell"]),
                        Path("pyproject.toml"): ConfigEntry(keys=["tool", "codespell"]),
                    },
                ),
                ConfigItem(
                    description="Ignore long base64 strings",
                    root={
                        Path(".codespellrc"): ConfigEntry(
                            keys=["codespell", "ignore-regex"],
                            get_value=lambda: "[A-Za-z0-9+/]{100,}",
                        ),
                        Path("setup.cfg"): ConfigEntry(
                            keys=["codespell", "ignore-regex"],
                            get_value=lambda: "[A-Za-z0-9+/]{100,}",
                        ),
                        Path("pyproject.toml"): ConfigEntry(
                            keys=["tool", "codespell", "ignore-regex"],
                            get_value=lambda: ["[A-Za-z0-9+/]{100,}"],
                        ),
                    },
                ),
                ConfigItem(
                    description="Ignore Words List",
                    root={
                        Path(".codespellrc"): ConfigEntry(
                            keys=["codespell", "ignore-words-list"],
                            get_value=lambda: "...",
                        ),
                        Path("setup.cfg"): ConfigEntry(
                            keys=["codespell", "ignore-words-list"],
                            get_value=lambda: "...",
                        ),
                        Path("pyproject.toml"): ConfigEntry(
                            keys=["tool", "codespell", "ignore-words-list"],
                            get_value=lambda: ["..."],
                        ),
                    },
                ),
            ],
        )

    def print_how_to_use(self) -> None:
        how_print(f"Run '{self.how_to_use_cmd()}' to run the {self.name} spellchecker.")
