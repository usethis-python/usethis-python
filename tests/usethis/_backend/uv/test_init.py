from pathlib import Path

from _test import change_cwd
from usethis._backend.uv.init import opinionated_uv_init
from usethis._config import usethis_config
from usethis._config_file import files_manager
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._types.build_backend import BuildBackendEnum


class TestOpinionatedUVINit:
    def test_build_backend_is_hatch(self, tmp_path: Path):
        with change_cwd(tmp_path), files_manager():
            manager = PyprojectTOMLManager()
            # Act
            opinionated_uv_init()

            # Assert
            assert manager[["build-system", "build-backend"]] == "hatchling.build"

    def test_build_backend_is_uv(self, tmp_path: Path):
        with (
            change_cwd(tmp_path),
            files_manager(),
            usethis_config.set(build_backend=BuildBackendEnum.uv),
        ):
            manager = PyprojectTOMLManager()
            # Act
            opinionated_uv_init()

            # Assert
            assert manager[["build-system", "build-backend"]] == "uv_build"
