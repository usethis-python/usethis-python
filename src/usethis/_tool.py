from abc import abstractmethod
from pathlib import Path
from typing import Protocol

from usethis._console import box_print, info_print, tick_print
from usethis._integrations.bitbucket.anchor import (
    ScriptItemAnchor as BitbucketScriptItemAnchor,
)
from usethis._integrations.bitbucket.schema import Script as BitbucketScript
from usethis._integrations.bitbucket.schema import Step as BitbucketStep
from usethis._integrations.pre_commit.hooks import (
    add_repo,
    get_hook_names,
    remove_hook,
)
from usethis._integrations.pre_commit.schema import (
    FileType,
    FileTypes,
    HookDefinition,
    Language,
    LocalRepo,
    UriRepo,
)
from usethis._integrations.project.layout import get_source_dir_str
from usethis._integrations.pyproject_toml.config import PyprojectConfig
from usethis._integrations.pyproject_toml.core import (
    PyprojectTOMLValueAlreadySetError,
    PyprojectTOMLValueMissingError,
    do_pyproject_id_keys_exist,
    remove_pyproject_value,
    set_pyproject_value,
)
from usethis._integrations.pyproject_toml.remove import remove_pyproject_toml
from usethis._integrations.uv.deps import (
    Dependency,
    add_deps_to_group,
    is_dep_in_any_group,
    remove_deps_from_group,
)


class Tool(Protocol):
    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the tool, for display purposes.

        It is assumed that this name is also the name of the Python package associated
        with the tool; if not, make sure to override methods which access this property.
        """

    def get_bitbucket_steps(self) -> list[BitbucketStep]:
        """Get the Bitbucket pipeline step associated with this tool."""
        return []

    def get_dev_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        """The tool's development dependencies.

        These should all be considered characteristic of this particular tool.

        Args:
            unconditional: Whether to return all possible dependencies regardless of
                           whether they are relevant to the current project.
        """
        return []

    def get_test_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        """The tool's test dependencies.

        These should all be considered characteristic of this particular tool.

        Args:
            unconditional: Whether to return all possible dependencies regardless of
                           whether they are relevant to the current project.
        """
        return []

    def get_pre_commit_repos(self) -> list[LocalRepo | UriRepo]:
        """Get the pre-commit repository configurations for the tool."""
        return []

    def get_pyproject_configs(self) -> list[PyprojectConfig]:
        """Get the pyproject configurations for the tool.

        All configuration keys returned by this method must be sub-keys of the
        keys returned by get_pyproject_id_keys().
        """
        return []

    def get_associated_ruff_rules(self) -> list[str]:
        """Get the Ruff rule codes associated with the tool."""
        return []

    def get_managed_files(self) -> list[Path]:
        """Get (relative) paths to files managed by the tool."""
        return []

    def get_managed_pyproject_keys(self) -> list[list[str]]:
        """Get keys for any pyproject.toml sections only used by this tool (not shared)."""
        return []

    @abstractmethod
    def print_how_to_use(self) -> None:
        """Print instructions for using the tool.

        This method is called after a tool is added to the project.
        """
        pass

    def is_used(self) -> bool:
        """Whether the tool is being used in the current project.

        Three heuristics are used by default:
        1. Whether any of the tool's characteristic dev dependencies are in the project.
        2. Whether any of the tool's managed files are in the project.
        3. Whether any of the tool's managed pyproject.toml sections are present.
        """
        for file in self.get_managed_files():
            if file.exists() and file.is_file():
                return True
        for id_keys in self.get_managed_pyproject_keys():
            if do_pyproject_id_keys_exist(id_keys):
                return True
        for dep in self.get_dev_deps(unconditional=True):
            if is_dep_in_any_group(dep):
                return True
        for dep in self.get_test_deps(unconditional=True):
            if is_dep_in_any_group(dep):
                return True

        return False

    def add_dev_deps(self) -> None:
        add_deps_to_group(self.get_dev_deps(), "dev")

    def remove_dev_deps(self) -> None:
        remove_deps_from_group(self.get_dev_deps(unconditional=True), "dev")

    def add_test_deps(self) -> None:
        add_deps_to_group(self.get_test_deps(), "test")

    def remove_test_deps(self) -> None:
        remove_deps_from_group(self.get_test_deps(unconditional=True), "test")

    def add_pre_commit_repo_configs(self) -> None:
        """Add the tool's pre-commit configuration."""
        repos = self.get_pre_commit_repos()

        if not repos:
            return

        # Add the config for this specific tool.
        for repo_config in repos:
            if repo_config.hooks is None:
                continue

            if len(repo_config.hooks) > 1:
                msg = "Multiple hooks in a single repo not yet supported."
                raise NotImplementedError(msg)

            for hook in repo_config.hooks:
                if hook.id not in get_hook_names():
                    # This will remove the placeholder, if present.
                    add_repo(repo_config)

    def remove_pre_commit_repo_configs(self) -> None:
        """Remove the tool's pre-commit configuration.

        If the .pre-commit-config.yaml file does not exist, this method has no effect.
        """
        repo_configs = self.get_pre_commit_repos()

        if not repo_configs:
            return

        for repo_config in repo_configs:
            if repo_config.hooks is None:
                continue

            # Remove the config for this specific tool.
            for hook in repo_config.hooks:
                if hook.id in get_hook_names():
                    remove_hook(hook.id)

    def add_pyproject_configs(self) -> None:
        """Add the tool's pyproject.toml configurations."""
        configs = self.get_pyproject_configs()
        if not configs:
            return

        first_addition = True
        for config in configs:
            try:
                set_pyproject_value(config.id_keys, config.value)
            except PyprojectTOMLValueAlreadySetError:
                pass
            else:
                if first_addition:
                    tick_print(f"Adding {self.name} config to 'pyproject.toml'.")
                    first_addition = False

    def remove_pyproject_configs(self) -> None:
        """Remove all pyproject.toml configurations associated with this tool.

        This includes any tool-specific sections in the pyproject.toml file.
        If no configurations exist, this method has no effect.
        """
        # Collect all keys to remove
        keys_to_remove = [
            config.id_keys for config in self.get_pyproject_configs()
        ] + self.get_managed_pyproject_keys()

        # Try to remove the first key to trigger the message
        first_removal = True
        for keys in keys_to_remove:
            try:
                remove_pyproject_value(keys)
            except PyprojectTOMLValueMissingError:
                pass
            else:
                if first_removal:
                    tick_print(f"Removing {self.name} config from 'pyproject.toml'.")
                    first_removal = False

    def remove_managed_files(self) -> None:
        """Remove all files managed by this tool.

        This includes any tool-specific files in the project.
        If no files exist, this method has no effect.
        """
        for file in self.get_managed_files():
            if (Path.cwd() / file).exists() and (Path.cwd() / file).is_file():
                tick_print(f"Removing '{file}'.")
                file.unlink()


class CodespellTool(Tool):
    @property
    def name(self) -> str:
        return "Codespell"

    def get_dev_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        return [Dependency(name="codespell")]

    def print_how_to_use(self) -> None:
        if PreCommitTool().is_used():
            box_print(
                "Run 'pre-commit run codespell --all-files' to run the Codespell spellchecker."
            )
        else:
            box_print("Run 'codespell' to run the Codespell spellchecker.")

    def get_pyproject_configs(self) -> list[PyprojectConfig]:
        return [
            PyprojectConfig(
                id_keys=["tool", "codespell"],
                value={
                    "ignore-regex": [
                        "[A-Za-z0-9+/]{100,}"  # Ignore long base64 strings
                    ],
                },
            ),
        ]

    def get_pre_commit_repos(self) -> list[LocalRepo | UriRepo]:
        return [
            UriRepo(
                repo="https://github.com/codespell-project/codespell",
                rev="v2.4.1",  # Manually bump this version when necessary
                hooks=[
                    HookDefinition(id="codespell", additional_dependencies=["tomli"])
                ],
            )
        ]

    def get_managed_pyproject_keys(self) -> list[list[str]]:
        return [["tool", "codespell"]]

    def get_managed_files(self) -> list[Path]:
        return [Path(".codespellrc")]

    def get_bitbucket_steps(self) -> list[BitbucketStep]:
        return [
            BitbucketStep(
                name="Run Codespell",
                caches=["uv"],
                script=BitbucketScript(
                    [
                        BitbucketScriptItemAnchor(name="install-uv"),
                        "uv run codespell",
                    ]
                ),
            )
        ]


class CoverageTool(Tool):
    @property
    def name(self) -> str:
        return "coverage"

    def get_test_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        deps = [Dependency(name="coverage", extras=frozenset({"toml"}))]
        if unconditional or PytestTool().is_used():
            deps += [Dependency(name="pytest-cov")]
        return deps

    def print_how_to_use(self) -> None:
        if PytestTool().is_used():
            box_print("Run 'pytest --cov' to run your tests with coverage.")
        else:
            box_print("Run 'coverage help' to see available coverage commands.")

    def get_pyproject_configs(self) -> list[PyprojectConfig]:
        return [
            PyprojectConfig(
                id_keys=["tool", "coverage", "run"],
                value={
                    "source": [get_source_dir_str()],
                    "omit": ["*/pytest-of-*/*"],
                },
            ),
            PyprojectConfig(
                id_keys=["tool", "coverage", "report"],
                value={
                    "exclude_also": [
                        "if TYPE_CHECKING:",
                        "raise AssertionError",
                        "raise NotImplementedError",
                        "assert_never(.*)",
                        "class .*\\bProtocol\\):",
                        "@(abc\\.)?abstractmethod",
                    ]
                },
            ),
        ]

    def get_managed_pyproject_keys(self) -> list[list[str]]:
        return [["tool", "coverage"]]

    def get_managed_files(self) -> list[Path]:
        return [Path(".coveragerc")]


class DeptryTool(Tool):
    @property
    def name(self) -> str:
        return "deptry"

    def get_dev_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        return [Dependency(name="deptry")]

    def print_how_to_use(self) -> None:
        _dir = get_source_dir_str()
        box_print(f"Run 'deptry {_dir}' to run deptry.")

    def get_pre_commit_repos(self) -> list[LocalRepo | UriRepo]:
        _dir = get_source_dir_str()
        return [
            LocalRepo(
                repo="local",
                hooks=[
                    HookDefinition(
                        id="deptry",
                        name="deptry",
                        entry=f"uv run --frozen deptry {_dir}",
                        language=Language("system"),
                        always_run=True,
                        pass_filenames=False,
                    )
                ],
            )
        ]

    def get_managed_pyproject_keys(self) -> list[list[str]]:
        return [["tool", "deptry"]]

    def get_bitbucket_steps(self) -> list[BitbucketStep]:
        _dir = get_source_dir_str()
        return [
            BitbucketStep(
                name="Run Deptry",
                caches=["uv"],
                script=BitbucketScript(
                    [
                        BitbucketScriptItemAnchor(name="install-uv"),
                        f"uv run deptry {_dir}",
                    ]
                ),
            )
        ]


class PreCommitTool(Tool):
    @property
    def name(self) -> str:
        return "pre-commit"

    def get_dev_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        return [Dependency(name="pre-commit")]

    def print_how_to_use(self) -> None:
        box_print("Run 'pre-commit run --all-files' to run the hooks manually.")

    def get_managed_files(self) -> list[Path]:
        return [Path(".pre-commit-config.yaml")]

    def get_bitbucket_steps(self) -> list[BitbucketStep]:
        return [
            BitbucketStep(
                name="Run pre-commit",
                caches=["uv", "pre-commit"],
                script=BitbucketScript(
                    [
                        BitbucketScriptItemAnchor(name="install-uv"),
                        "uv run pre-commit run --all-files",
                    ]
                ),
            )
        ]


class PyprojectFmtTool(Tool):
    @property
    def name(self) -> str:
        return "pyproject-fmt"

    def get_dev_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        return [Dependency(name="pyproject-fmt")]

    def print_how_to_use(self) -> None:
        if PreCommitTool().is_used():
            box_print(
                "Run 'pre-commit run pyproject-fmt --all-files' to run pyproject-fmt."
            )
        else:
            box_print("Run 'pyproject-fmt pyproject.toml' to run pyproject-fmt.")

    def get_pre_commit_repos(self) -> list[LocalRepo | UriRepo]:
        return [
            UriRepo(
                repo="https://github.com/tox-dev/pyproject-fmt",
                rev="v2.5.0",  # Manually bump this version when necessary
                hooks=[HookDefinition(id="pyproject-fmt")],
            )
        ]

    def get_pyproject_configs(self) -> list[PyprojectConfig]:
        return [
            PyprojectConfig(
                id_keys=["tool", "pyproject-fmt"],
                value={"keep_full_version": True},
            )
        ]

    def get_managed_pyproject_keys(self) -> list[list[str]]:
        return [["tool", "pyproject-fmt"]]

    def get_bitbucket_steps(self) -> list[BitbucketStep]:
        return [
            BitbucketStep(
                name="Run pyproject-fmt",
                caches=["uv"],
                script=BitbucketScript(
                    [
                        BitbucketScriptItemAnchor(name="install-uv"),
                        "uv run pyproject-fmt pyproject.toml",
                    ]
                ),
            )
        ]


class PyprojectTOMLTool(Tool):
    @property
    def name(self) -> str:
        return "pyproject.toml"

    def get_dev_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        return []

    def print_how_to_use(self) -> None:
        box_print("Populate 'pyproject.toml' with the project configuration.")
        info_print(
            "Learn more at https://packaging.python.org/en/latest/guides/writing-pyproject-toml/"
        )

    def get_managed_files(self) -> list[Path]:
        return [
            Path("pyproject.toml"),
        ]

    def remove_managed_files(self) -> None:
        remove_pyproject_toml()
        return super().remove_managed_files()


class PytestTool(Tool):
    @property
    def name(self) -> str:
        return "pytest"

    def get_test_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        deps = [Dependency(name="pytest")]
        if unconditional or CoverageTool().is_used():
            deps += [Dependency(name="pytest-cov")]
        return deps

    def print_how_to_use(self) -> None:
        box_print(
            "Add test files to the '/tests' directory with the format 'test_*.py'."
        )
        box_print("Add test functions with the format 'test_*()'.")
        box_print("Run 'pytest' to run the tests.")

    def get_extra_dev_deps(self) -> list[Dependency]:
        return [Dependency(name="pytest-cov")]

    def get_pyproject_configs(self) -> list[PyprojectConfig]:
        return [
            PyprojectConfig(
                id_keys=["tool", "pytest"],
                value={
                    "ini_options": {
                        "testpaths": ["tests"],
                        "addopts": [
                            "--import-mode=importlib",  # Now recommended https://docs.pytest.org/en/7.1.x/explanation/goodpractices.html#which-import-mode
                        ],
                        "filterwarnings": ["error"],
                    }
                },
            ),
        ]

    def get_associated_ruff_rules(self) -> list[str]:
        return ["PT"]

    def get_managed_pyproject_keys(self) -> list[list[str]]:
        return [["tool", "pytest"]]

    def get_managed_files(self) -> list[Path]:
        return [Path("tests/conftest.py")]


class RequirementsTxtTool(Tool):
    @property
    def name(self) -> str:
        return "requirements.txt"

    def get_dev_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        return []

    def print_how_to_use(self) -> None:
        if PreCommitTool().is_used():
            box_print("Run the 'pre-commit run uv-export' to write 'requirements.txt'.")
        else:
            box_print(
                "Run 'uv export --no-dev --output-file=requirements.txt' to write 'requirements.txt'."
            )

    def get_pre_commit_repos(self) -> list[LocalRepo | UriRepo]:
        return [
            LocalRepo(
                repo="local",
                hooks=[
                    HookDefinition(
                        id="uv-export",
                        name="uv-export",
                        files="^uv\\.lock$",
                        pass_filenames=False,
                        entry="uv export --frozen --no-dev --output-file=requirements.txt --quiet",
                        language=Language("system"),
                        require_serial=True,
                    )
                ],
            )
        ]

    def get_managed_files(self) -> list[Path]:
        return [Path("requirements.txt")]


class RuffTool(Tool):
    @property
    def name(self) -> str:
        return "Ruff"

    def get_dev_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        return [Dependency(name="ruff")]

    def print_how_to_use(self) -> None:
        box_print("Run 'ruff check --fix' to run the Ruff linter with autofixes.")
        box_print("Run 'ruff format' to run the Ruff formatter.")

    def get_pre_commit_repos(self) -> list[LocalRepo | UriRepo]:
        return [
            LocalRepo(
                repo="local",
                hooks=[
                    HookDefinition(
                        id="ruff-format",
                        name="ruff-format",
                        entry="uv run --frozen ruff format --force-exclude",
                        language=Language("system"),
                        types_or=FileTypes(
                            [FileType("python"), FileType("pyi"), FileType("jupyter")]
                        ),
                        always_run=True,
                        require_serial=True,
                    ),
                ],
            ),
            LocalRepo(
                repo="local",
                hooks=[
                    HookDefinition(
                        id="ruff",
                        name="ruff",
                        entry="uv run --frozen ruff check --fix --force-exclude",
                        language=Language("system"),
                        types_or=FileTypes(
                            [FileType("python"), FileType("pyi"), FileType("jupyter")]
                        ),
                        always_run=True,
                        require_serial=True,
                    ),
                ],
            ),
        ]

    def get_pyproject_configs(self) -> list[PyprojectConfig]:
        return [
            PyprojectConfig(
                id_keys=["tool", "ruff"],
                value={
                    "line-length": 88,
                    "lint": {"select": []},
                },
            )
        ]

    def get_managed_pyproject_keys(self) -> list[list[str]]:
        return [["tool", "ruff"]]

    def get_managed_files(self) -> list[Path]:
        return [Path("ruff.toml"), Path(".ruff.toml")]

    def get_bitbucket_steps(self) -> list[BitbucketStep]:
        return [
            BitbucketStep(
                name="Run Ruff",
                caches=["uv"],
                script=BitbucketScript(
                    [
                        BitbucketScriptItemAnchor(name="install-uv"),
                        "uv run ruff check --fix",
                        "uv run ruff format",
                    ]
                ),
            )
        ]


ALL_TOOLS: list[Tool] = [
    CodespellTool(),
    CoverageTool(),
    DeptryTool(),
    PreCommitTool(),
    PyprojectTOMLTool(),
    PyprojectFmtTool(),
    PytestTool(),
    RequirementsTxtTool(),
    RuffTool(),
]
