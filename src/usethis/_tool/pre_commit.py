"""Pre-commit hook specification types for tools."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel
from typing_extensions import assert_never

from usethis._backend.dispatch import get_backend
from usethis._integrations.pre_commit import schema
from usethis._integrations.pre_commit.language import get_system_language
from usethis._types.backend import BackendEnum

if TYPE_CHECKING:
    from typing_extensions import Self


class PreCommitRepoConfig(BaseModel):
    """Configuration for a single pre-commit repository.

    Attributes:
        repo: The repository definition to be used for pre-commit hooks.
        requires_venv: Whether the repository requires a virtual environment to run.
    """

    repo: schema.LocalRepo | schema.UriRepo
    requires_venv: bool


class PreCommitConfig(BaseModel):
    """Configuration for pre-commit repositories.

    Attributes:
        repo_configs: A list of pre-commit repository configurations.
        inform_how_to_use_on_migrate: Whether to inform the user how to use the
                                      associated tool if migrating to or from using this
                                      pre-commit configuration versus using an approach
                                      that involves installing the tool directly to the
                                      project environment. This is useful to turn off
                                      for cases where it is possible to call the command
                                      directly without pre-commit and this is more
                                      succinct.
    """

    repo_configs: list[PreCommitRepoConfig]
    inform_how_to_use_on_migrate: bool = True

    @classmethod
    def from_single_repo(
        cls,
        repo: schema.LocalRepo | schema.UriRepo,
        *,
        requires_venv: bool,
        inform_how_to_use_on_migrate: bool = True,
    ) -> Self:
        return cls(
            repo_configs=[
                PreCommitRepoConfig(
                    repo=repo,
                    requires_venv=requires_venv,
                )
            ],
            inform_how_to_use_on_migrate=inform_how_to_use_on_migrate,
        )

    @classmethod
    def from_system_hook(
        cls,
        *,
        hook_id: str,
        entry: str,
        pass_filenames: bool | None = None,
        always_run: bool | None = None,
        require_serial: bool | None = None,
    ) -> Self:
        """Create a PreCommitConfig for a local system hook.

        Handles backend dispatch internally: for the uv backend, the entry is
        prefixed with ``uv run --frozen --offline``.

        Args:
            hook_id: The hook identifier; also used as the hook display name.
            entry: The base command to run (without uv prefix).
            pass_filenames: Whether to pass filenames to the hook.
            always_run: Whether to always run the hook.
            require_serial: Whether to require serial execution.
        """
        backend: Literal[BackendEnum.uv, BackendEnum.none] = get_backend()
        if backend is BackendEnum.uv:
            full_entry = f"uv run --frozen --offline {entry}"
        elif backend is BackendEnum.none:
            full_entry = entry
        else:
            assert_never(backend)

        return cls.from_single_repo(
            schema.LocalRepo(
                repo="local",
                hooks=[
                    schema.HookDefinition(
                        id=hook_id,
                        name=hook_id,
                        entry=full_entry,
                        language=get_system_language(),
                        pass_filenames=pass_filenames,
                        always_run=always_run,
                        require_serial=require_serial,
                    )
                ],
            ),
            requires_venv=True,
            inform_how_to_use_on_migrate=False,
        )

    @property
    def any_require_venv(self) -> bool:
        return any(repo_config.requires_venv for repo_config in self.repo_configs)
