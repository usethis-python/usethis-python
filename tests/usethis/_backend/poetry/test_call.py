from pathlib import Path

import pytest

import usethis._backend.poetry.call
from usethis._backend.poetry.call import call_poetry_subprocess
from usethis._backend.poetry.errors import PoetrySubprocessFailedError
from usethis._config import usethis_config
from usethis._config_file import files_manager
from usethis._file.pyproject_toml.write import prepare_pyproject_write
from usethis._subprocess import SubprocessFailedError
from usethis._test import change_cwd
from usethis._types.backend import BackendEnum
from usethis.errors import ForbiddenBackendError


class TestCallPoetrySubprocess:
    def test_forbidden_when_uv_backend(self):
        with (
            usethis_config.set(backend=BackendEnum.uv),
            pytest.raises(ForbiddenBackendError),
        ):
            call_poetry_subprocess(["--version"], change_toml=False)

    def test_forbidden_when_none_backend(self):
        with (
            usethis_config.set(backend=BackendEnum.none),
            pytest.raises(ForbiddenBackendError),
        ):
            call_poetry_subprocess(["--version"], change_toml=False)

    def test_allowed_when_poetry_backend(self, tmp_path: Path):
        with usethis_config.set(backend=BackendEnum.poetry, project_dir=tmp_path):
            output = call_poetry_subprocess(["--version"], change_toml=False)
        assert "Poetry" in output

    def test_allowed_when_auto_backend(self, tmp_path: Path):
        with usethis_config.set(backend=BackendEnum.auto, project_dir=tmp_path):
            output = call_poetry_subprocess(["--version"], change_toml=False)
        assert "Poetry" in output

    def test_version_not_quieted(self, monkeypatch: pytest.MonkeyPatch):
        """The --version command should not have --quiet added."""

        def mock_call_subprocess(args: list[str], **__: object) -> str:
            return " ".join(args)

        monkeypatch.setattr(
            usethis._backend.poetry.call,
            "call_subprocess",
            mock_call_subprocess,
        )

        with usethis_config.set(backend=BackendEnum.poetry):
            result = call_poetry_subprocess(["--version"], change_toml=False)

        assert "--quiet" not in result
        assert "--no-interaction" in result

    def test_non_version_command_quieted(self, monkeypatch: pytest.MonkeyPatch):
        """Non-version commands should have --quiet added."""

        def mock_call_subprocess(args: list[str], **__: object) -> str:
            return " ".join(args)

        monkeypatch.setattr(
            usethis._backend.poetry.call,
            "call_subprocess",
            mock_call_subprocess,
        )

        with usethis_config.set(backend=BackendEnum.poetry):
            result = call_poetry_subprocess(["add", "pytest"], change_toml=False)

        assert "--quiet" in result
        assert "--no-interaction" in result

    def test_verbose_mode(self, monkeypatch: pytest.MonkeyPatch):
        """When subprocess_verbose is True, -vvv should be added instead of --quiet."""

        def mock_call_subprocess(args: list[str], **__: object) -> str:
            return " ".join(args)

        monkeypatch.setattr(
            usethis._backend.poetry.call,
            "call_subprocess",
            mock_call_subprocess,
        )

        with usethis_config.set(backend=BackendEnum.poetry, subprocess_verbose=True):
            result = call_poetry_subprocess(["add", "pytest"], change_toml=False)

        assert "-vvv" in result
        assert "--quiet" not in result

    def test_subprocess_failure_raises(self, monkeypatch: pytest.MonkeyPatch):
        def mock_call_subprocess(*_: object, **__: object) -> str:
            msg = "mock failure"
            raise SubprocessFailedError(msg)

        monkeypatch.setattr(
            usethis._backend.poetry.call,
            "call_subprocess",
            mock_call_subprocess,
        )

        with (
            usethis_config.set(backend=BackendEnum.poetry),
            pytest.raises(PoetrySubprocessFailedError),
        ):
            call_poetry_subprocess(["add", "pytest"], change_toml=False)

    def test_file_not_found_raises(self, monkeypatch: pytest.MonkeyPatch):
        def mock_call_subprocess(*_: object, **__: object) -> str:
            raise FileNotFoundError

        monkeypatch.setattr(
            usethis._backend.poetry.call,
            "call_subprocess",
            mock_call_subprocess,
        )

        with (
            usethis_config.set(backend=BackendEnum.poetry),
            pytest.raises(
                PoetrySubprocessFailedError,
                match="Poetry is not installed",
            ),
        ):
            call_poetry_subprocess(["add", "pytest"], change_toml=False)

    def test_frozen_adds_lock_for_add(self, monkeypatch: pytest.MonkeyPatch):
        """When frozen=True, --lock should be added to 'add' commands."""

        def mock_call_subprocess(args: list[str], **__: object) -> str:
            return " ".join(args)

        monkeypatch.setattr(
            usethis._backend.poetry.call,
            "call_subprocess",
            mock_call_subprocess,
        )

        with usethis_config.set(backend=BackendEnum.poetry, frozen=True):
            result = call_poetry_subprocess(["add", "pytest"], change_toml=False)

        assert result == "poetry --quiet --no-interaction add --lock pytest"

    def test_frozen_adds_lock_for_remove(self, monkeypatch: pytest.MonkeyPatch):
        """When frozen=True, --lock should be added to 'remove' commands."""

        def mock_call_subprocess(args: list[str], **__: object) -> str:
            return " ".join(args)

        monkeypatch.setattr(
            usethis._backend.poetry.call,
            "call_subprocess",
            mock_call_subprocess,
        )

        with usethis_config.set(backend=BackendEnum.poetry, frozen=True):
            result = call_poetry_subprocess(
                ["remove", "--group", "test", "pytest"], change_toml=False
            )

        assert (
            result
            == "poetry --quiet --no-interaction remove --lock --group test pytest"
        )

    def test_frozen_no_lock_for_version(self, monkeypatch: pytest.MonkeyPatch):
        """When frozen=True, --lock should not be added to non-add/remove commands."""

        def mock_call_subprocess(args: list[str], **__: object) -> str:
            return " ".join(args)

        monkeypatch.setattr(
            usethis._backend.poetry.call,
            "call_subprocess",
            mock_call_subprocess,
        )

        with usethis_config.set(backend=BackendEnum.poetry, frozen=True):
            result = call_poetry_subprocess(["--version"], change_toml=False)

        assert "--lock" not in result

    def test_not_frozen_no_lock_for_add(self, monkeypatch: pytest.MonkeyPatch):
        """When frozen=False, --lock should not be added to 'add' commands."""

        def mock_call_subprocess(args: list[str], **__: object) -> str:
            return " ".join(args)

        monkeypatch.setattr(
            usethis._backend.poetry.call,
            "call_subprocess",
            mock_call_subprocess,
        )

        with usethis_config.set(backend=BackendEnum.poetry, frozen=False):
            result = call_poetry_subprocess(["add", "pytest"], change_toml=False)

        assert "--lock" not in result

    def test_frozen_restores_existing_lockfile(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """When frozen=True and poetry.lock exists, it should be restored after the subprocess."""
        lock_path = tmp_path / "poetry.lock"
        original_content = "original-lock-content"
        lock_path.write_text(original_content)

        created_dirs: list[str] = []
        original_mkdtemp = usethis._backend.poetry.call.tempfile.mkdtemp

        def tracking_mkdtemp(
            suffix: str | None = None,
            prefix: str | None = None,
            dir: str | None = None,  # noqa: A002
        ) -> str:
            result = original_mkdtemp(suffix=suffix, prefix=prefix, dir=dir)
            created_dirs.append(result)
            return result

        monkeypatch.setattr(
            usethis._backend.poetry.call.tempfile,
            "mkdtemp",
            tracking_mkdtemp,
        )

        def mock_call_subprocess(*_: object, **__: object) -> str:
            # Simulate poetry modifying the lockfile
            lock_path.write_text("modified-lock-content")
            return ""

        monkeypatch.setattr(
            usethis._backend.poetry.call,
            "call_subprocess",
            mock_call_subprocess,
        )

        with usethis_config.set(
            backend=BackendEnum.poetry, frozen=True, project_dir=tmp_path
        ):
            call_poetry_subprocess(["add", "pytest"], change_toml=False)

        assert lock_path.read_text() == original_content
        # Verify the temporary backup directory was cleaned up
        assert len(created_dirs) == 1
        assert not Path(created_dirs[0]).exists()

    def test_frozen_removes_created_lockfile(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """When frozen=True and poetry.lock didn't exist, any new lockfile should be removed."""
        lock_path = tmp_path / "poetry.lock"
        assert not lock_path.exists()

        def mock_call_subprocess(*_: object, **__: object) -> str:
            # Simulate poetry creating a new lockfile
            lock_path.write_text("new-lock-content")
            return ""

        monkeypatch.setattr(
            usethis._backend.poetry.call,
            "call_subprocess",
            mock_call_subprocess,
        )

        with usethis_config.set(
            backend=BackendEnum.poetry, frozen=True, project_dir=tmp_path
        ):
            call_poetry_subprocess(["add", "pytest"], change_toml=False)

        assert not lock_path.exists()

    def test_frozen_restores_lockfile_on_failure(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """When frozen=True and the subprocess fails, poetry.lock should still be restored."""
        lock_path = tmp_path / "poetry.lock"
        original_content = "original-lock-content"
        lock_path.write_text(original_content)

        def mock_call_subprocess(*_: object, **__: object) -> str:
            lock_path.write_text("modified-lock-content")
            msg = "mock failure"
            raise SubprocessFailedError(msg)

        monkeypatch.setattr(
            usethis._backend.poetry.call,
            "call_subprocess",
            mock_call_subprocess,
        )

        with (
            usethis_config.set(
                backend=BackendEnum.poetry, frozen=True, project_dir=tmp_path
            ),
            pytest.raises(PoetrySubprocessFailedError),
        ):
            call_poetry_subprocess(["add", "pytest"], change_toml=False)

        assert lock_path.read_text() == original_content

    def test_not_frozen_does_not_restore_lockfile(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """When frozen=False, poetry.lock changes should be preserved."""
        lock_path = tmp_path / "poetry.lock"
        lock_path.write_text("original-lock-content")

        def mock_call_subprocess(*_: object, **__: object) -> str:
            lock_path.write_text("modified-lock-content")
            return ""

        monkeypatch.setattr(
            usethis._backend.poetry.call,
            "call_subprocess",
            mock_call_subprocess,
        )

        with usethis_config.set(
            backend=BackendEnum.poetry, frozen=False, project_dir=tmp_path
        ):
            call_poetry_subprocess(["add", "pytest"], change_toml=False)

        assert lock_path.read_text() == "modified-lock-content"

    def test_change_toml_rereads_when_locked(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """When change_toml=True and manager is locked, the file should be re-read."""
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "test"\nversion = "0.1.0"\n'
        )

        def mock_call_subprocess(*_: object, **__: object) -> str:
            return ""

        monkeypatch.setattr(
            usethis._backend.poetry.call,
            "call_subprocess",
            mock_call_subprocess,
        )

        with (
            change_cwd(tmp_path),
            usethis_config.set(backend=BackendEnum.poetry),
            files_manager(),
        ):
            call_poetry_subprocess(["add", "pytest"], change_toml=True)

    def test_change_toml_false_no_prepare(self, monkeypatch: pytest.MonkeyPatch):
        """When change_toml=False, prepare_pyproject_write should not be called."""
        called = False

        original_prepare = prepare_pyproject_write

        def mock_prepare():
            nonlocal called
            called = True
            original_prepare()

        monkeypatch.setattr(
            usethis._backend.poetry.call,
            "prepare_pyproject_write",
            mock_prepare,
        )

        def mock_call_subprocess(*_: object, **__: object) -> str:
            return ""

        monkeypatch.setattr(
            usethis._backend.poetry.call,
            "call_subprocess",
            mock_call_subprocess,
        )

        with usethis_config.set(backend=BackendEnum.poetry):
            call_poetry_subprocess(["--version"], change_toml=False)

        assert not called


class TestPreparePyprojectWrite:
    def test_pyproject_exists_and_locked(self, tmp_path: Path):
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "test"\nversion = "0.1.0"\n'
        )

        with (
            change_cwd(tmp_path),
            files_manager(),
        ):
            prepare_pyproject_write()

    def test_no_pyproject_and_locked(self, tmp_path: Path):
        with (
            change_cwd(tmp_path),
            files_manager(),
        ):
            prepare_pyproject_write()

    def test_pyproject_exists_not_locked(self, tmp_path: Path):
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "test"\nversion = "0.1.0"\n'
        )

        with change_cwd(tmp_path):
            prepare_pyproject_write()

    def test_no_pyproject_not_locked(self, tmp_path: Path):
        with change_cwd(tmp_path):
            prepare_pyproject_write()
