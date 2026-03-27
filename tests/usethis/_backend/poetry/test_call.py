from pathlib import Path

import pytest

from usethis._backend.poetry.call import call_poetry_subprocess
from usethis._backend.poetry.errors import PoetrySubprocessFailedError
from usethis._config import usethis_config
from usethis._types.backend import BackendEnum
from usethis.errors import ForbiddenBackendError


class TestCallPoetrySubprocess:
    def test_forbidden_when_uv_backend(self):
        with usethis_config.set(backend=BackendEnum.uv):
            with pytest.raises(ForbiddenBackendError):
                call_poetry_subprocess(["--version"], change_toml=False)

    def test_forbidden_when_none_backend(self):
        with usethis_config.set(backend=BackendEnum.none):
            with pytest.raises(ForbiddenBackendError):
                call_poetry_subprocess(["--version"], change_toml=False)

    def test_allowed_when_poetry_backend(self, tmp_path: Path):
        # Poetry may or may not be installed, so we just check it doesn't raise
        # ForbiddenBackendError
        with usethis_config.set(backend=BackendEnum.poetry, project_dir=tmp_path):
            try:
                call_poetry_subprocess(["--version"], change_toml=False)
            except PoetrySubprocessFailedError:
                pass  # Poetry not installed, but backend check passed

    def test_allowed_when_auto_backend(self, tmp_path: Path):
        with usethis_config.set(backend=BackendEnum.auto, project_dir=tmp_path):
            try:
                call_poetry_subprocess(["--version"], change_toml=False)
            except PoetrySubprocessFailedError:
                pass  # Poetry not installed, but backend check passed
