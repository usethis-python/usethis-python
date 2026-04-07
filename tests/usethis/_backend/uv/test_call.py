from pathlib import Path

import pytest

import usethis._backend.uv.call
from _test import change_cwd
from usethis._backend.uv.call import call_uv_subprocess
from usethis._backend.uv.errors import UVSubprocessFailedError
from usethis._config import usethis_config
from usethis._config_file import files_manager
from usethis._subprocess import SubprocessResult


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
        def mock_call_subprocess(
            args: list[str], *, cwd: Path | None = None
        ) -> SubprocessResult:
            _ = cwd
            return SubprocessResult(" ".join(args), "")

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
            ) == ("uv run --no-progress --frozen pre-commit install")

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
requires-python = ">=3.10"
"""
        )

        # Act
        with change_cwd(tmp_path), files_manager():
            call_uv_subprocess(["add", "ruff==0.9.0"], change_toml=True)

        # Assert
        assert (
            (tmp_path / "pyproject.toml").read_text()
            == """\
[project]
name = "example"
requires-python = ">=3.10"
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

    def test_stderr_warnings_surfaced(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capfd: pytest.CaptureFixture[str],
    ):
        """Warnings emitted on stderr by uv should be surfaced via warn_print."""

        def mock_call_subprocess(
            args: list[str], *, cwd: Path | None = None
        ) -> SubprocessResult:
            _ = args, cwd
            return SubprocessResult("", "warning: something went wrong\n")

        monkeypatch.setattr(
            usethis._backend.uv.call,
            "call_subprocess",
            mock_call_subprocess,
        )

        # Act
        call_uv_subprocess(["help"], change_toml=False)

        # Assert
        out, err = capfd.readouterr()
        assert "something went wrong" in out
        assert not err

    def test_empty_stderr_no_warning(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capfd: pytest.CaptureFixture[str],
    ):
        """When stderr is empty, no warning should be printed."""

        def mock_call_subprocess(
            args: list[str], *, cwd: Path | None = None
        ) -> SubprocessResult:
            _ = args, cwd
            return SubprocessResult("", "")

        monkeypatch.setattr(
            usethis._backend.uv.call,
            "call_subprocess",
            mock_call_subprocess,
        )

        # Act
        call_uv_subprocess(["help"], change_toml=False)

        # Assert
        out, err = capfd.readouterr()
        assert out == ""
        assert err == ""

    def test_multiline_stderr_warnings(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capfd: pytest.CaptureFixture[str],
    ):
        """Multiple warning lines on stderr should each be surfaced."""

        def mock_call_subprocess(
            args: list[str], *, cwd: Path | None = None
        ) -> SubprocessResult:
            _ = args, cwd
            return SubprocessResult("", "warning: first\nwarning: second\n")

        monkeypatch.setattr(
            usethis._backend.uv.call,
            "call_subprocess",
            mock_call_subprocess,
        )

        # Act
        call_uv_subprocess(["help"], change_toml=False)

        # Assert
        out, err = capfd.readouterr()
        assert "first" in out
        assert "second" in out
        assert not err

    def test_non_warning_stderr_not_surfaced(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capfd: pytest.CaptureFixture[str],
    ):
        """Non-warning lines on stderr should not be surfaced."""

        def mock_call_subprocess(
            args: list[str], *, cwd: Path | None = None
        ) -> SubprocessResult:
            _ = args, cwd
            return SubprocessResult("", "Resolved 31 packages in 265ms\n")

        monkeypatch.setattr(
            usethis._backend.uv.call,
            "call_subprocess",
            mock_call_subprocess,
        )

        # Act
        call_uv_subprocess(["help"], change_toml=False)

        # Assert
        out, err = capfd.readouterr()
        assert out == ""
        assert err == ""

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_unpinned_dep_warning_surfaced(
        self,
        tmp_path: Path,
        capfd: pytest.CaptureFixture[str],
    ):
        """An unpinned dependency should trigger a uv warning that gets surfaced."""

        # Arrange - init a lib project
        with change_cwd(tmp_path):
            call_uv_subprocess(["init", "--lib", "--vcs", "none"], change_toml=True)

        # Add an unpinned dependency directly to pyproject.toml (no lower bound)
        pyproject_path = tmp_path / "pyproject.toml"
        content = pyproject_path.read_text()
        content = content.replace("dependencies = []", 'dependencies = ["usethis"]')
        pyproject_path.write_text(content)

        # Act - sync with lowest-direct resolution to trigger the warning
        with change_cwd(tmp_path):
            call_uv_subprocess(
                ["sync", "--resolution=lowest-direct"], change_toml=False
            )

        # Assert - the unpinned dependency warning should be surfaced
        out, _err = capfd.readouterr()
        assert "unpinned" in out.lower()
