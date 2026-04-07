from pathlib import Path

import pytest

from _test import change_cwd
from usethis._backend.uv.call import call_uv_subprocess
from usethis._config import UsethisConfig, usethis_config
from usethis._types.backend import BackendEnum
from usethis._types.build_backend import BuildBackendEnum
from usethis.errors import ForbiddenBackendError


class TestUsethisConfig:
    class TestCopy:
        def test_returns_new_instance(self):
            # Arrange
            config = UsethisConfig()

            # Act
            copied = config.copy()

            # Assert
            assert copied is not config

        def test_preserves_defaults(self):
            # Arrange
            config = UsethisConfig()

            # Act
            copied = config.copy()

            # Assert
            assert copied.offline == config.offline
            assert copied.quiet == config.quiet
            assert copied.frozen == config.frozen
            assert copied.backend == config.backend

        def test_preserves_modified_values(self):
            # Arrange
            config = UsethisConfig()
            config.offline = True
            config.quiet = True
            config.frozen = True
            config.alert_only = True
            config.instruct_only = True
            config.backend = BackendEnum.uv
            config.inferred_backend = BackendEnum.uv
            config.build_backend = BuildBackendEnum.uv
            config.disable_pre_commit = True
            config.subprocess_verbose = True
            config.project_dir = Path("/some/project")

            # Act
            copied = config.copy()

            # Assert
            assert copied.offline is True
            assert copied.quiet is True
            assert copied.frozen is True
            assert copied.alert_only is True
            assert copied.instruct_only is True
            assert copied.backend is BackendEnum.uv
            assert copied.inferred_backend is BackendEnum.uv
            assert copied.build_backend is BuildBackendEnum.uv
            assert copied.disable_pre_commit is True
            assert copied.subprocess_verbose is True
            assert copied.project_dir == Path("/some/project")

        def test_independent_of_original(self):
            # Arrange
            config = UsethisConfig()

            # Act
            copied = config.copy()
            copied.offline = True

            # Assert
            assert config.offline is False

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

    class TestSetRestoresOnException:
        def test_restores_quiet_on_exception(self):
            # Arrange
            config = UsethisConfig()
            assert config.quiet is False

            # Act
            with pytest.raises(RuntimeError), config.set(quiet=True):
                raise RuntimeError

            # Assert
            assert config.quiet is False

        def test_restores_all_fields_on_exception(self, tmp_path: Path):
            # Arrange
            config = UsethisConfig()
            old = config.copy()

            # Act
            with (
                pytest.raises(RuntimeError),
                config.set(
                    offline=True,
                    quiet=True,
                    frozen=True,
                    alert_only=True,
                    instruct_only=True,
                    backend=BackendEnum.none,
                    build_backend=BuildBackendEnum.uv,
                    disable_pre_commit=True,
                    subprocess_verbose=True,
                    project_dir=tmp_path,
                ),
            ):
                raise RuntimeError

            # Assert
            assert config.offline == old.offline
            assert config.quiet == old.quiet
            assert config.frozen == old.frozen
            assert config.alert_only == old.alert_only
            assert config.instruct_only == old.instruct_only
            assert config.backend == old.backend
            assert config.build_backend == old.build_backend
            assert config.disable_pre_commit == old.disable_pre_commit
            assert config.subprocess_verbose == old.subprocess_verbose
            assert config.project_dir == old.project_dir

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
