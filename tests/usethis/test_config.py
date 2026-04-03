from pathlib import Path

import pytest

from usethis._backend.uv.call import call_uv_subprocess
from usethis._config import UsethisConfig, usethis_config
from usethis._test import change_cwd
from usethis._types.backend import BackendEnum
from usethis.errors import ForbiddenBackendError


class TestUsethisConfig:
    class TestCPD:
        def test_matches_path_cwd(self, tmp_path: Path):
            # Arrange
            config = UsethisConfig()

            # Act
            with change_cwd(tmp_path):
                cwd = config.cpd()

            # Assert
            assert cwd == tmp_path

        def test_set_overrides_cwd(self, tmp_path: Path):
            # Arrange
            config = UsethisConfig()

            # Act
            with (
                change_cwd(tmp_path),
                config.set(project_dir=Path("42 Wallaby Way, Sydney")),
            ):
                project_dir = config.cpd()

            # Assert
            assert project_dir == Path("42 Wallaby Way, Sydney")

    class TestDisableUVSubprocess:
        def test_raises_error_when_disabled(self):
            # Act & Assert
            with (
                change_cwd(Path.cwd()),
                usethis_config.set(backend=BackendEnum.none),
                pytest.raises(ForbiddenBackendError),
            ):
                call_uv_subprocess(["python", "list"], change_toml=False)

        def test_does_not_raise_error_when_enabled(self):
            # Act & Assert
            with (
                change_cwd(Path.cwd()),
                usethis_config.set(backend=BackendEnum.uv),
            ):
                output = call_uv_subprocess(["python", "list"], change_toml=False)

            assert output is not None

    class TestFrozenAndNoSync:
        def test_both_accepted(self):
            with usethis_config.set(frozen=True, no_sync=True):
                assert usethis_config.frozen
                assert usethis_config.no_sync

        def test_no_error_when_only_frozen(self):
            with usethis_config.set(frozen=True, no_sync=False):
                assert usethis_config.frozen
                assert not usethis_config.no_sync

        def test_no_error_when_only_no_sync(self):
            with usethis_config.set(frozen=False, no_sync=True):
                assert not usethis_config.frozen
                assert usethis_config.no_sync
