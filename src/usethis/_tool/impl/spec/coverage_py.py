"""Coverage.py tool specification."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, final

from typing_extensions import override

from usethis._config import usethis_config
from usethis._config_file import (
    DotCoverageRCManager,
    DotCoverageRCTOMLManager,
    ToxINIManager,
)
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._file.setup_cfg.io_ import SetupCFGManager
from usethis._integrations.project.layout import get_source_dir_str
from usethis._tool.base import ToolMeta, ToolSpec
from usethis._tool.config import ConfigEntry, ConfigItem, ConfigSpec

if TYPE_CHECKING:
    from usethis._file.manager import Document, KeyValueFileManager


class CoveragePyToolSpec(ToolSpec):
    @final
    @property
    @override
    def meta(self) -> ToolMeta:
        return ToolMeta(
            name="Coverage.py",
            url="https://github.com/nedbat/coveragepy",
            managed_files=[Path(".coveragerc"), Path(".coveragerc.toml")],
        )

    @override
    @final
    def preferred_file_manager(self) -> KeyValueFileManager[Document]:
        if (usethis_config.cpd() / "pyproject.toml").exists():
            return PyprojectTOMLManager()
        return DotCoverageRCManager()

    @override
    @final
    def config_spec(self) -> ConfigSpec:
        # https://coverage.readthedocs.io/en/latest/config.html#configuration-reference
        # But the `latest` link doesn't yet include some latest changes regarding
        # `.coveragerc.toml`, which are available here:
        # https://coverage.readthedocs.io/en/7.13.0/config.html#configuration-reference

        exclude_also = [
            "if TYPE_CHECKING:",
            "raise AssertionError",
            "raise NotImplementedError",
            'msg = ".*"',
            "assert_never(.*)",
            "class .*\\bProtocol\\):",
            "@(abc\\.)?abstractmethod",
        ]
        omit = ["*/pytest-of-*/*"]

        def _get_source():
            return [get_source_dir_str()]

        return ConfigSpec.from_flat(
            file_managers=[
                DotCoverageRCManager(),
                DotCoverageRCTOMLManager(),
                SetupCFGManager(),
                ToxINIManager(),
                PyprojectTOMLManager(),
            ],
            resolution="first",
            config_items=[
                ConfigItem(
                    description="Overall Config",
                    root={
                        Path(".coveragerc"): ConfigEntry(keys=[]),
                        Path(".coveragerc.toml"): ConfigEntry(keys=[]),
                        # N.B. other ini files use a "coverage:" prefix so there's no
                        # section corresponding to overall config
                        Path("pyproject.toml"): ConfigEntry(keys=["tool", "coverage"]),
                    },
                    applies_to_all=False,
                ),
                ConfigItem(
                    description="Run Configuration",
                    root={
                        Path(".coveragerc"): ConfigEntry(keys=["run"]),
                        Path(".coveragerc.toml"): ConfigEntry(keys=["run"]),
                        Path("setup.cfg"): ConfigEntry(keys=["coverage:run"]),
                        Path("tox.ini"): ConfigEntry(keys=["coverage:run"]),
                        Path("pyproject.toml"): ConfigEntry(
                            keys=["tool", "coverage", "run"]
                        ),
                    },
                ),
                ConfigItem(
                    description="Source Configuration",
                    root={
                        Path(".coveragerc"): ConfigEntry(
                            keys=["run", "source"], get_value=_get_source
                        ),
                        Path(".coveragerc.toml"): ConfigEntry(
                            keys=["run", "source"],
                            get_value=_get_source,
                        ),
                        Path("setup.cfg"): ConfigEntry(
                            keys=["coverage:run", "source"], get_value=_get_source
                        ),
                        Path("tox.ini"): ConfigEntry(
                            keys=["coverage:run", "source"], get_value=_get_source
                        ),
                        Path("pyproject.toml"): ConfigEntry(
                            keys=["tool", "coverage", "run", "source"],
                            get_value=_get_source,
                        ),
                    },
                ),
                ConfigItem(
                    # https://github.com/usethis-python/usethis-python/issues/930
                    # This config helps ensure reports generated in CI environments
                    # have consistent paths between jobs, by forcing them to be relative
                    description="Relative Files Configuration",
                    root={
                        Path(".coveragerc"): ConfigEntry(
                            keys=["run", "relative_files"], get_value=lambda: "true"
                        ),
                        Path(".coveragerc.toml"): ConfigEntry(
                            keys=["run", "relative_files"], get_value=lambda: True
                        ),
                        Path("setup.cfg"): ConfigEntry(
                            keys=["coverage:run", "relative_files"],
                            get_value=lambda: "true",
                        ),
                        Path("tox.ini"): ConfigEntry(
                            keys=["coverage:run", "relative_files"],
                            get_value=lambda: "true",
                        ),
                        Path("pyproject.toml"): ConfigEntry(
                            keys=["tool", "coverage", "run", "relative_files"],
                            get_value=lambda: True,
                        ),
                    },
                ),
                ConfigItem(
                    description="Report Configuration",
                    root={
                        Path(".coveragerc"): ConfigEntry(keys=["report"]),
                        Path(".coveragerc.toml"): ConfigEntry(keys=["report"]),
                        Path("setup.cfg"): ConfigEntry(keys=["coverage:report"]),
                        Path("tox.ini"): ConfigEntry(keys=["coverage:report"]),
                        Path("pyproject.toml"): ConfigEntry(
                            keys=["tool", "coverage", "report"]
                        ),
                    },
                ),
                ConfigItem(
                    description="Exclude Also Configuration",
                    root={
                        Path(".coveragerc"): ConfigEntry(
                            keys=["report", "exclude_also"],
                            get_value=lambda: exclude_also,
                        ),
                        Path(".coveragerc.toml"): ConfigEntry(
                            keys=["report", "exclude_also"],
                            get_value=lambda: exclude_also,
                        ),
                        Path("setup.cfg"): ConfigEntry(
                            keys=["coverage:report", "exclude_also"],
                            get_value=lambda: exclude_also,
                        ),
                        Path("tox.ini"): ConfigEntry(
                            keys=["coverage:report", "exclude_also"],
                            get_value=lambda: exclude_also,
                        ),
                        Path("pyproject.toml"): ConfigEntry(
                            keys=["tool", "coverage", "report", "exclude_also"],
                            get_value=lambda: exclude_also,
                        ),
                    },
                ),
                ConfigItem(
                    description="Omit Configuration",
                    root={
                        Path(".coveragerc"): ConfigEntry(
                            keys=["report", "omit"], get_value=lambda: omit
                        ),
                        Path(".coveragerc.toml"): ConfigEntry(
                            keys=["report", "omit"],
                            get_value=lambda: omit,
                        ),
                        Path("setup.cfg"): ConfigEntry(
                            keys=["coverage:report", "omit"], get_value=lambda: omit
                        ),
                        Path("tox.ini"): ConfigEntry(
                            keys=["coverage:report", "omit"], get_value=lambda: omit
                        ),
                        Path("pyproject.toml"): ConfigEntry(
                            keys=["tool", "coverage", "report", "omit"],
                            get_value=lambda: omit,
                        ),
                    },
                ),
                ConfigItem(
                    description="Paths Configuration",
                    root={
                        Path(".coveragerc"): ConfigEntry(keys=["paths"]),
                        Path(".coveragerc.toml"): ConfigEntry(keys=["paths"]),
                        Path("setup.cfg"): ConfigEntry(keys=["coverage:paths"]),
                        Path("tox.ini"): ConfigEntry(keys=["coverage:paths"]),
                        Path("pyproject.toml"): ConfigEntry(
                            keys=["tool", "coverage", "paths"],
                        ),
                    },
                ),
                ConfigItem(
                    description="HTML Configuration",
                    root={
                        Path(".coveragerc"): ConfigEntry(keys=["html"]),
                        Path(".coveragerc.toml"): ConfigEntry(keys=["html"]),
                        Path("setup.cfg"): ConfigEntry(keys=["coverage:html"]),
                        Path("tox.ini"): ConfigEntry(keys=["coverage:html"]),
                        Path("pyproject.toml"): ConfigEntry(
                            keys=["tool", "coverage", "html"]
                        ),
                    },
                ),
                ConfigItem(
                    description="XML Configuration",
                    root={
                        Path(".coveragerc"): ConfigEntry(keys=["xml"]),
                        Path(".coveragerc.toml"): ConfigEntry(keys=["xml"]),
                        Path("setup.cfg"): ConfigEntry(keys=["coverage:xml"]),
                        Path("tox.ini"): ConfigEntry(keys=["coverage:xml"]),
                        Path("pyproject.toml"): ConfigEntry(
                            keys=["tool", "coverage", "xml"]
                        ),
                    },
                ),
                ConfigItem(
                    description="JSON Configuration",
                    root={
                        Path(".coveragerc"): ConfigEntry(keys=["json"]),
                        Path(".coveragerc.toml"): ConfigEntry(keys=["json"]),
                        Path("setup.cfg"): ConfigEntry(keys=["coverage:json"]),
                        Path("tox.ini"): ConfigEntry(keys=["coverage:json"]),
                        Path("pyproject.toml"): ConfigEntry(
                            keys=["tool", "coverage", "json"]
                        ),
                    },
                ),
                ConfigItem(
                    description="LCOV Configuration",
                    root={
                        Path(".coveragerc"): ConfigEntry(keys=["lcov"]),
                        Path(".coveragerc.toml"): ConfigEntry(keys=["lcov"]),
                        Path("setup.cfg"): ConfigEntry(keys=["coverage:lcov"]),
                        Path("tox.ini"): ConfigEntry(keys=["coverage:lcov"]),
                        Path("pyproject.toml"): ConfigEntry(
                            keys=["tool", "coverage", "lcov"]
                        ),
                    },
                ),
            ],
        )
