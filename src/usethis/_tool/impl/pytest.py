from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

from typing_extensions import assert_never

from usethis._config import usethis_config
from usethis._config_file import DotPytestINIManager, PytestINIManager, ToxINIManager
from usethis._console import how_print, info_print, instruct_print
from usethis._integrations.backend.dispatch import get_backend
from usethis._integrations.backend.uv.used import is_uv_used
from usethis._integrations.ci.bitbucket.anchor import (
    ScriptItemAnchor as BitbucketScriptItemAnchor,
)
from usethis._integrations.ci.bitbucket.schema import Image, ImageName
from usethis._integrations.ci.bitbucket.schema import Script as BitbucketScript
from usethis._integrations.ci.bitbucket.schema import Step as BitbucketStep
from usethis._integrations.ci.bitbucket.steps import get_steps_in_default
from usethis._integrations.ci.bitbucket.used import is_bitbucket_used
from usethis._integrations.environ.python import get_supported_major_python_versions
from usethis._integrations.file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._integrations.file.setup_cfg.io_ import SetupCFGManager
from usethis._integrations.project.build import has_pyproject_toml_declared_build_system
from usethis._integrations.project.layout import get_source_dir_str
from usethis._tool.base import Tool
from usethis._tool.config import ConfigEntry, ConfigItem, ConfigSpec
from usethis._tool.rule import RuleConfig
from usethis._types.backend import BackendEnum
from usethis._types.deps import Dependency

if TYPE_CHECKING:
    from usethis._io import KeyValueFileManager

_PYTEST_PIP_CMD = "pip install pytest"


class PytestTool(Tool):
    # https://github.com/pytest-dev/pytest
    @property
    def name(self) -> str:
        return "pytest"

    def print_how_to_use(self) -> None:
        how_print(
            "Add test files to the '/tests' directory with the format 'test_*.py'."
        )
        how_print("Add test functions with the format 'test_*()'.")

        backend = get_backend()
        if backend is BackendEnum.uv and is_uv_used():
            how_print("Run 'uv run pytest' to run the tests.")
        else:
            assert backend in (BackendEnum.none, BackendEnum.uv)
            how_print("Run 'pytest' to run the tests.")

    def get_test_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        from usethis._tool.impl.coverage_py import CoveragePyTool

        deps = [Dependency(name="pytest")]
        if unconditional or CoveragePyTool().is_used():
            deps += [Dependency(name="pytest-cov")]
        return deps

    def preferred_file_manager(self) -> KeyValueFileManager:
        if (usethis_config.cpd() / "pyproject.toml").exists():
            return PyprojectTOMLManager()
        return PytestINIManager()

    def get_config_spec(self) -> ConfigSpec:
        # https://docs.pytest.org/en/stable/reference/customize.html#configuration-file-formats
        # "Options from multiple configfiles candidates are never merged - the first match wins."

        # Much of what follows is recommended here (sp-repo-review):
        # https://learn.scientific-python.org/development/guides/pytest/#configuring-pytest
        value = {
            "testpaths": ["tests"],
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

    def get_managed_files(self) -> list[Path]:
        return [Path(".pytest.ini"), Path("pytest.ini"), Path("tests/conftest.py")]

    def get_rule_config(self) -> RuleConfig:
        return RuleConfig(selected=["PT"])

    def get_active_config_file_managers(self) -> set[KeyValueFileManager]:
        # This is a variant of the "first" method
        config_spec = self.get_config_spec()
        if config_spec.resolution != "bespoke":
            # Something has gone badly wrong, perhaps in a subclass of PytestTool.
            raise NotImplementedError
        # As per https://docs.pytest.org/en/stable/reference/customize.html#finding-the-rootdir
        # Files will only be matched for configuration if:
        # - pytest.ini: will always match and take precedence, even if empty.
        # - pyproject.toml: contains a [tool.pytest.ini_options] table.
        # - tox.ini: contains a [pytest] section.
        # - setup.cfg: contains a [tool:pytest] section.
        # Finally, a pyproject.toml file will be considered the configfile if no other
        # match was found, in this case even if it does not contain a
        # [tool.pytest.ini_options] table
        # Also, the docs mention that the hidden .pytest.ini variant is allowed, in my
        # experimentation is takes precedence over pyproject.toml but not pytest.ini.

        for (
            relative_path,
            file_manager,
        ) in config_spec.file_manager_by_relative_path.items():
            path = usethis_config.cpd() / relative_path
            if path.exists() and path.is_file():
                if isinstance(file_manager, PyprojectTOMLManager):
                    if ["tool", "pytest", "ini_options"] in file_manager:
                        return {file_manager}
                    else:
                        continue
                return {file_manager}

        # Second chance for pyproject.toml
        for (
            relative_path,
            file_manager,
        ) in config_spec.file_manager_by_relative_path.items():
            path = usethis_config.cpd() / relative_path
            if (
                path.exists()
                and path.is_file()
                and isinstance(file_manager, PyprojectTOMLManager)
            ):
                return {file_manager}

        file_managers = config_spec.file_manager_by_relative_path.values()
        if not file_managers:
            return set()

        # Use the preferred default file since there's no existing file.
        preferred_file_manager = self.preferred_file_manager()
        if preferred_file_manager not in file_managers:
            msg = (
                f"The preferred file manager '{preferred_file_manager}' is not "
                f"among the file managers '{file_managers}' for the tool "
                f"'{self.name}'."
            )
            raise NotImplementedError(msg)
        return {preferred_file_manager}

    def get_bitbucket_steps(self) -> list[BitbucketStep]:
        versions = get_supported_major_python_versions()

        backend = get_backend()

        steps = []
        for version in versions:
            if backend is BackendEnum.uv:
                step = BitbucketStep(
                    name=f"Test on 3.{version}",
                    caches=["uv"],
                    script=BitbucketScript(
                        [
                            BitbucketScriptItemAnchor(name="install-uv"),
                            f"uv run --python 3.{version} pytest -x --junitxml=test-reports/report.xml",
                        ]
                    ),
                )
            elif backend is BackendEnum.none:
                step = BitbucketStep(
                    name=f"Test on 3.{version}",
                    image=Image(ImageName(f"python:3.{version}")),
                    script=BitbucketScript(
                        [
                            BitbucketScriptItemAnchor(name="ensure-venv"),
                            _PYTEST_PIP_CMD,
                            "pytest -x --junitxml=test-reports/report.xml",
                        ]
                    ),
                )
            else:
                assert_never(backend)

            steps.append(step)
        return steps

    def get_managed_bitbucket_step_names(self) -> list[str]:
        names = set()
        for step in get_steps_in_default():
            if step.name is not None:
                match = re.match(r"^Test on 3\.\d{1,2}$", step.name)
                if match:
                    names.add(step.name)

        for step in self.get_bitbucket_steps():
            if step.name is not None:
                names.add(step.name)

        return sorted(names)

    def update_bitbucket_steps(self) -> None:
        """Update the pytest-related Bitbucket pipelines steps.

        A bespoke function is needed here to ensure we inform the user about the need
        to manually add the dependencies if they are not using a backend.
        """
        # Same early exit as the wrapped super() function
        if not is_bitbucket_used() or not self.is_used():
            return

        # But otherwise if not early exiting, we are going to add steps so we might
        # need to inform the user
        super().update_bitbucket_steps()

        backend = get_backend()

        if backend is BackendEnum.uv:
            pass
        elif backend is BackendEnum.none:
            if usethis_config.backend is BackendEnum.auto:
                info_print(
                    "Consider installing 'uv' to readily manage test dependencies."
                )
            instruct_print(
                "Declare your test dependencies in 'bitbucket-pipelines.yml'."
            )
            info_print(f"Add test dependencies to this line: '{_PYTEST_PIP_CMD}'")
            pass
        else:
            assert_never(backend)
