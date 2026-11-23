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

    class TestNoSync:
        def test_no_sync(self):
            # Act
            with usethis_config.set(frozen=False, offline=False):
                result = call_uv_subprocess(
                    ["add", "--group", "dev", "ruff"], change_toml=False, no_sync=True
                )

            # Assert
            assert result == "uv add --no-progress --no-sync --group dev ruff"

        def test_sync_by_default(self):
            # Act
            with usethis_config.set(frozen=False, offline=False):
                result = call_uv_subprocess(
                    ["add", "--group", "dev", "ruff"], change_toml=False
                )

            # Assert
            assert result == "uv add --no-progress --group dev ruff"

        def test_frozen(self):
            # Act
            with usethis_config.set(frozen=True, offline=False):
                result = call_uv_subprocess(
                    ["add", "--group", "dev", "ruff"], change_toml=False, no_sync=True
                )

            # Assert
            # Nothing is synced when frozen, so there is nothing to skip
            assert result == "uv add --no-progress --frozen --group dev ruff"

        @pytest.mark.parametrize(
            ("args", "expected"),
            [
                (
                    ["add", "--group", "dev", "ruff"],
                    "uv add --no-progress --no-sync --group dev ruff",
                ),
                (
                    ["remove", "--group", "dev", "ruff"],
                    "uv remove --no-progress --no-sync --group dev ruff",
                ),
                (
                    ["run", "pre-commit", "install"],
                    "uv run --no-progress --no-sync pre-commit install",
                ),
            ],
        )
        def test_supported_commands(self, args: list[str], expected: str):
            # Act
            with usethis_config.set(frozen=False, offline=False):
                result = call_uv_subprocess(args, change_toml=False, no_sync=True)

            # Assert
            assert result == expected

        def test_unsupported_command(self):
            # Act
            with usethis_config.set(frozen=False, offline=False):
                result = call_uv_subprocess(["sync"], change_toml=False, no_sync=True)

            # Assert
            # The option is ignored, rather than passing on one which uv would reject
            assert result == "uv sync --no-progress"

        @pytest.fixture(autouse=True)
        def _echo_args(self, monkeypatch: pytest.MonkeyPatch) -> None:
            """Mock subprocess calls so that the arguments passed to them are returned."""

            def mock_call_subprocess(
                args: list[str], *, cwd: Path | None = None
            ) -> SubprocessResult:
                _ = cwd
                return SubprocessResult(" ".join(args), "")

            monkeypatch.setattr(
                usethis._backend.uv.call, "call_subprocess", mock_call_subprocess
            )

    class TestGroups:
        def test_groups(self):
            # Act
            with usethis_config.set(frozen=False, offline=False):
                result = call_uv_subprocess(
                    ["sync"], change_toml=False, groups=["dev", "test"]
                )

            # Assert
            assert result == "uv sync --no-progress --group dev --group test"

        def test_none_by_default(self):
            # Act
            with usethis_config.set(frozen=False, offline=False):
                result = call_uv_subprocess(["sync"], change_toml=False)

            # Assert
            assert result == "uv sync --no-progress"

        def test_empty(self):
            # Act
            with usethis_config.set(frozen=False, offline=False):
                result = call_uv_subprocess(["sync"], change_toml=False, groups=[])

            # Assert
            assert result == "uv sync --no-progress"

        def test_frozen(self):
            # Act
            with usethis_config.set(frozen=True, offline=False):
                result = call_uv_subprocess(["sync"], change_toml=False, groups=["dev"])

            # Assert
            assert result == "uv sync --no-progress --group dev --frozen"

        @pytest.mark.parametrize(
            ("args", "expected"),
            [
                (["sync"], "uv sync --no-progress --group dev"),
                (
                    ["run", "pre-commit", "install"],
                    "uv run --no-progress --group dev pre-commit install",
                ),
                (
                    ["export", "--no-hashes"],
                    "uv export --no-progress --group dev --no-hashes",
                ),
                (["tree"], "uv tree --no-progress --group dev"),
            ],
        )
        def test_supported_commands(self, args: list[str], expected: str):
            # Act
            with usethis_config.set(frozen=False, offline=False):
                result = call_uv_subprocess(args, change_toml=False, groups=["dev"])

            # Assert
            assert result == expected

        @pytest.mark.parametrize(
            ("args", "expected"),
            [
                (
                    ["add", "ruff"],
                    "uv add --no-progress ruff",
                ),
                (
                    ["remove", "ruff"],
                    "uv remove --no-progress ruff",
                ),
                (["lock"], "uv lock --no-progress"),
            ],
        )
        def test_unsupported_commands(self, args: list[str], expected: str):
            # Act
            with usethis_config.set(frozen=False, offline=False):
                result = call_uv_subprocess(args, change_toml=False, groups=["dev"])

            # Assert
            # The option is ignored: for add and remove, it would name the group to
            # modify, rather than one to include
            assert result == expected

        @pytest.fixture(autouse=True)
        def _echo_args(self, monkeypatch: pytest.MonkeyPatch) -> None:
            """Mock subprocess calls so that the arguments passed to them are returned."""

            def mock_call_subprocess(
                args: list[str], *, cwd: Path | None = None
            ) -> SubprocessResult:
                _ = cwd
                return SubprocessResult(" ".join(args), "")

            monkeypatch.setattr(
                usethis._backend.uv.call, "call_subprocess", mock_call_subprocess
            )

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
        assert out == "⚠ something went wrong\n"
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
        assert out == "⚠ first\n⚠ second\n"
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
