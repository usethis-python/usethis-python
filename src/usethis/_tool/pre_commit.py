from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel

from usethis._integrations.pre_commit.schema import LocalRepo, UriRepo

if TYPE_CHECKING:
    from typing_extensions import Self


class PreCommitRepoConfig(BaseModel):
    """Configuration for a single pre-commit repository.

    Attributes:
        repo: The repository definition to be used for pre-commit hooks.
        requires_venv: Whether the repository requires a virtual environment to run.
    """

    repo: LocalRepo | UriRepo
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
        repo: LocalRepo | UriRepo,
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

    @property
    def any_require_venv(self) -> bool:
        return any(repo_config.requires_venv for repo_config in self.repo_configs)
