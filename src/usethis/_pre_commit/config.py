from typing import Literal

from pydantic import BaseModel


class HookConfig(BaseModel):
    id: str
    name: str
    entry: str | None = None
    language: Literal["system", "python"] | None = None
    always_run: bool | None = None
    pass_filenames: bool | None = None
    additional_dependencies: list[str] | None = None


class PreCommitRepoConfig(BaseModel):
    repo: str
    rev: str | None = None
    hooks: list[HookConfig]
