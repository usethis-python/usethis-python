"""pytest tool specification."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, final

from typing_extensions import assert_never, override

from usethis._backend.uv.detect import is_uv_used
from usethis._config import usethis_config
from usethis._config_file import DotPytestINIManager, PytestINIManager, ToxINIManager
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._file.setup_cfg.io_ import SetupCFGManager
from usethis._integrations.project.build import has_pyproject_toml_declared_build_system
from usethis._integrations.project.layout import get_source_dir_str, get_tests_dir_str
from usethis._tool.base import ToolMeta, ToolSpec
from usethis._tool.config import ConfigEntry, ConfigItem, ConfigSpec
from usethis._tool.rule import RuleConfig

if TYPE_CHECKING:
    from usethis._file.manager import Document, KeyValueFileManager


class PytestToolSpec(ToolSpec):
    @final
    @property
    @override
    def meta(self) -> ToolMeta:
        return ToolMeta(
            name="pytest",
            url="https://github.com/pytest-dev/pytest",
            managed_files=[
                Path(".pytest.ini"),
                Path("pytest.ini"),
            ],
            rule_config=RuleConfig(selected=["PT"], nontests_unmanaged_ignored=["PT"]),
        )

    @property
    @override
    def managed_files(self) -> list[Path]:
        tests_dir = get_tests_dir_str()
        return [*self.meta.managed_files, Path(tests_dir) / "conftest.py"]

    @override
    @final
    def raw_cmd(self) -> str:
        return "pytest"

    @override
    @final
    def preferred_file_manager(self) -> KeyValueFileManager[Document]:
        if (usethis_config.cpd() / "pyproject.toml").exists():
            return PyprojectTOMLManager()
        return PytestINIManager()

    @override
    @final
    def config_spec(self) -> ConfigSpec:
        # https://docs.pytest.org/en/stable/reference/customize.html#configuration-file-formats
        # "Options from multiple configfiles candidates are never merged - the first match wins."

        # Much of what follows is recommended here (sp-repo-review):
        # https://learn.scientific-python.org/development/guides/pytest/#configuring-pytest
        tests_dir = get_tests_dir_str()
        value = {
            "testpaths": [tests_dir],
            "addopts": [
                "--import-mode=importlib",  # Now recommended https://docs.pytest.org/en/7.1.x/explanation/goodpractices.html#which-import-mode
                "-ra",  # summary report of all results (sp-repo-review)
                # Not --showlocals", because it's too verbose in some cases (https://github.com/usethis-python/usethis-python/issues/527)
                "--strict-markers",  # fail on unknown markers (sp-repo-review)
                "--strict-config",  # fail on unknown config (sp-repo-review)
            ],
            "filterwarnings": ["error"],  # fail on warnings (sp-repo-review)
            "xfail_strict": True,  # fail on tests marked xfail (sp-repo-review)
            "log_cli_level": "INFO",  # include all >=INFO level log messages (sp-repo-review)
            "minversion": "7",  # minimum pytest version (sp-repo-review)
        }

        source_dir_str = get_source_dir_str()
        set_pythonpath = (
            not is_uv_used() or not has_pyproject_toml_declared_build_system()
        )
        if set_pythonpath:
            if source_dir_str == ".":
                value["pythonpath"] = []
            elif source_dir_str == "src":
                value["pythonpath"] = ["src"]
            else:
                assert_never(source_dir_str)

        value_ini = value.copy()
        # https://docs.pytest.org/en/stable/reference/reference.html#confval-xfail_strict
        value_ini["xfail_strict"] = "True"  # stringify boolean

        return ConfigSpec.from_flat(
            file_managers=[
                PytestINIManager(),
                DotPytestINIManager(),
                PyprojectTOMLManager(),
                ToxINIManager(),
                SetupCFGManager(),
            ],
            resolution="bespoke",
            config_items=[
                ConfigItem(
                    description="Overall Config",
                    root={
                        Path("pytest.ini"): ConfigEntry(keys=[]),
                        Path(".pytest.ini"): ConfigEntry(keys=[]),
                        Path("pyproject.toml"): ConfigEntry(keys=["tool", "pytest"]),
                        Path("tox.ini"): ConfigEntry(keys=["pytest"]),
                        Path("setup.cfg"): ConfigEntry(keys=["tool:pytest"]),
                    },
                ),
                ConfigItem(
                    description="INI-Style Options",
                    root={
                        Path("pytest.ini"): ConfigEntry(
                            keys=["pytest"], get_value=lambda: value_ini
                        ),
                        Path(".pytest.ini"): ConfigEntry(
                            keys=["pytest"], get_value=lambda: value_ini
                        ),
                        Path("pyproject.toml"): ConfigEntry(
                            keys=["tool", "pytest", "ini_options"],
                            get_value=lambda: value,
                        ),
                        Path("tox.ini"): ConfigEntry(
                            keys=["pytest"], get_value=lambda: value_ini
                        ),
                        Path("setup.cfg"): ConfigEntry(
                            keys=["tool:pytest"], get_value=lambda: value_ini
                        ),
                    },
                ),
            ],
        )
