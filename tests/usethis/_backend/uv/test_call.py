from pathlib import Path

import pytest

import usethis._backend.uv.call
from usethis._backend.uv.call import call_uv_subprocess
from usethis._backend.uv.errors import UVSubprocessFailedError
from usethis._config import usethis_config
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._test import change_cwd


class TestCallUVSubprocess:
    def test_help_output_suppressed(self, capfd: pytest.CaptureFixture[str]):
        # Act
        call_uv_subprocess(["help"], change_toml=False)

        # Assert
        assert capfd.readouterr().out == ""
        assert capfd.readouterr().err == ""

    def test_nonexistent_command(self):
        # Act and Assert
        match = ".*error: unrecognized subcommand 'does-not-exist'.*"
        with pytest.raises(UVSubprocessFailedError, match=match):
            call_uv_subprocess(["does-not-exist"], change_toml=False)

    def test_frozen_added_in_uv_run(self, monkeypatch: pytest.MonkeyPatch):
        # Mock the usethis._subprocess.call_subprocess function to check args passed

        # Arrange
        # Mock the call_subprocess function to check the args passed
        def mock_call_subprocess(args: list[str], *, cwd: Path | None = None) -> str:
            _ = cwd
            return " ".join(args)

        monkeypatch.setattr(
            usethis._backend.uv.call,
            "call_subprocess",
            mock_call_subprocess,
        )

        with usethis_config.set(frozen=True, offline=False):
            assert not usethis_config.subprocess_verbose
            # Act, Assert
            # Check the args passed to call_subprocess
            assert call_uv_subprocess(
                ["run", "pre-commit", "install"], change_toml=False
            ) == ("uv run --quiet --frozen pre-commit install")

    def test_no_sync_added_in_uv_add(self, monkeypatch: pytest.MonkeyPatch):
        # Arrange
        def mock_call_subprocess(args: list[str], *, cwd: Path | None = None) -> str:
            _ = cwd
            return " ".join(args)

        monkeypatch.setattr(
            usethis._backend.uv.call,
            "call_subprocess",
            mock_call_subprocess,
        )

        with usethis_config.set(no_sync=True, frozen=False, offline=False):
            # Act, Assert
            assert call_uv_subprocess(
                ["add", "--group", "test", "pytest"], change_toml=False
            ) == ("uv add --quiet --no-sync --group test pytest")

    def test_no_sync_added_in_uv_remove(self, monkeypatch: pytest.MonkeyPatch):
        # Arrange
        def mock_call_subprocess(args: list[str], *, cwd: Path | None = None) -> str:
            _ = cwd
            return " ".join(args)

        monkeypatch.setattr(
            usethis._backend.uv.call,
            "call_subprocess",
            mock_call_subprocess,
        )

        with usethis_config.set(no_sync=True, frozen=False, offline=False):
            # Act, Assert
            assert call_uv_subprocess(
                ["remove", "--group", "test", "pytest"], change_toml=False
            ) == ("uv remove --quiet --no-sync --group test pytest")

    def test_frozen_takes_precedence_over_no_sync(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        # Arrange
        def mock_call_subprocess(args: list[str], *, cwd: Path | None = None) -> str:
            _ = cwd
            return " ".join(args)

        monkeypatch.setattr(
            usethis._backend.uv.call,
            "call_subprocess",
            mock_call_subprocess,
        )

        with usethis_config.set(no_sync=True, frozen=True, offline=False):
            # Act, Assert
            # --frozen should take precedence, not --no-sync
            result = call_uv_subprocess(
                ["add", "--group", "test", "pytest"], change_toml=False
            )
            assert "--frozen" in result
            assert "--no-sync" not in result

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_handle_missing_version(
        self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
    ):
        # https://github.com/usethis-python/usethis-python/issues/299

        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[project]
name = "example"
"""
        )

        # Act
        with change_cwd(tmp_path), PyprojectTOMLManager():
            call_uv_subprocess(["add", "ruff==0.9.0"], change_toml=True)

        # Assert
        assert (
            (tmp_path / "pyproject.toml").read_text()
            == """\
[project]
name = "example"
version = "0.1.0"
dependencies = [
    "ruff==0.9.0",
]

[tool.uv]
link-mode = "symlink"
"""
        )
        out, err = capfd.readouterr()
        assert not err
        assert out == "✔ Setting project version to '0.1.0' in 'pyproject.toml'.\n"
