from pathlib import Path

from usethis._integrations.backend.uv.init import opinionated_uv_init
from usethis._integrations.file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._test import change_cwd


class TestOpinionatedUVINit:
    def test_build_backend_is_hatch(self, tmp_path: Path):
        with change_cwd(tmp_path), PyprojectTOMLManager() as manager:
            # Act
            opinionated_uv_init()

            # Assert
            assert manager[["build-system", "build-backend"]] == "hatchling.build"
