"""pytest tool implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, final

from typing_extensions import override

from usethis._config import usethis_config
from usethis._console import how_print
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._tool.base import Tool
from usethis._tool.heuristics import is_likely_used
from usethis._tool.impl.spec.coverage_py import CoveragePyToolSpec
from usethis._tool.impl.spec.pytest import PytestToolSpec
from usethis._types.deps import Dependency

if TYPE_CHECKING:
    from usethis._file.manager import KeyValueFileManager


@final
class PytestTool(PytestToolSpec, Tool):
    @override
    def test_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        deps = [Dependency(name="pytest")]
        if unconditional or is_likely_used(CoveragePyToolSpec()):
            deps += [Dependency(name="pytest-cov")]
        return deps

    @override
    def print_how_to_use(self) -> None:
        how_print(
            "Add test files to the '/tests' directory with the format 'test_*.py'."
        )
        how_print("Add test functions with the format 'test_*()'.")
        how_print(f"Run '{self.how_to_use_cmd()}' to run the tests.")

    @override
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
