from __future__ import annotations

import re
from typing import TYPE_CHECKING, final

from typing_extensions import assert_never

from usethis._backend.dispatch import get_backend
from usethis._config import usethis_config
from usethis._console import how_print, info_print, instruct_print
from usethis._detect.ci.bitbucket import is_bitbucket_used
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._integrations.ci.bitbucket import schema as bitbucket_schema
from usethis._integrations.ci.bitbucket.anchor import (
    ScriptItemAnchor as BitbucketScriptItemAnchor,
)
from usethis._integrations.ci.bitbucket.steps import get_steps_in_default
from usethis._integrations.environ.python import get_supported_minor_python_versions
from usethis._python.version import PythonVersion
from usethis._tool.base import Tool
from usethis._tool.heuristics import is_likely_used
from usethis._tool.impl.spec.coverage_py import CoveragePyToolSpec
from usethis._tool.impl.spec.pytest import PytestToolSpec
from usethis._types.backend import BackendEnum
from usethis._types.deps import Dependency

if TYPE_CHECKING:
    from usethis._io import KeyValueFileManager

_PYTEST_PIP_CMD = "pip install pytest"


@final
class PytestTool(PytestToolSpec, Tool):
    def test_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        deps = [Dependency(name="pytest")]
        if unconditional or is_likely_used(CoveragePyToolSpec()):
            deps += [Dependency(name="pytest-cov")]
        return deps

    def print_how_to_use(self) -> None:
        how_print(
            "Add test files to the '/tests' directory with the format 'test_*.py'."
        )
        how_print("Add test functions with the format 'test_*()'.")
        how_print(f"Run '{self.how_to_use_cmd()}' to run the tests.")

    def get_active_config_file_managers(self) -> set[KeyValueFileManager[object]]:
        # This is a variant of the "first" method
        config_spec = self.config_spec()
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

    def get_bitbucket_steps(
        self, *, matrix_python: bool = True
    ) -> list[bitbucket_schema.Step]:
        if matrix_python:
            versions = get_supported_minor_python_versions()
        else:
            versions = [PythonVersion.from_interpreter()]

        backend = get_backend()

        steps: list[bitbucket_schema.Step] = []
        for version in versions:
            if backend is BackendEnum.uv:
                step = bitbucket_schema.Step(
                    name=f"Test on {version.to_short_string()}",
                    caches=["uv"],
                    script=bitbucket_schema.Script(
                        [
                            BitbucketScriptItemAnchor(name="install-uv"),
                            f"uv run --python {version.to_short_string()} pytest -x --junitxml=test-reports/report.xml",
                        ]
                    ),
                )
            elif backend is BackendEnum.none:
                step = bitbucket_schema.Step(
                    name=f"Test on {version.to_short_string()}",
                    image=bitbucket_schema.Image(
                        bitbucket_schema.ImageName(
                            f"python:{version.to_short_string()}"
                        )
                    ),
                    script=bitbucket_schema.Script(
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
        names: set[str] = set()
        for step in get_steps_in_default():
            if step.name is not None:
                match = re.match(r"^Test on 3\.\d{1,2}$", step.name)
                if match:
                    names.add(step.name)

        for step in self.get_bitbucket_steps():
            if step.name is not None:
                names.add(step.name)

        return sorted(names)

    def update_bitbucket_steps(self, *, matrix_python: bool = True) -> None:
        """Update the pytest-related Bitbucket Pipelines steps.

        A bespoke function is needed here to ensure we inform the user about the need
        to manually add the dependencies if they are not using a backend.

        Unlike other tools, pytest steps should always be added even when pre-commit
        is used, because pytest is a test step, not a pre-commit hook.
        """
        # Same early exit as the wrapped super() function
        if not is_bitbucket_used() or not self.is_used():
            return

        # But otherwise if not early exiting, we are going to add steps so we might
        # need to inform the user
        # Call _unconditional_update_bitbucket_steps directly to bypass the
        # pre-commit check in the base class
        self._unconditional_update_bitbucket_steps(matrix_python=matrix_python)

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
