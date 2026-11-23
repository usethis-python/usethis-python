from pathlib import Path

import pytest

import usethis._backend.uv.call
from usethis._backend.uv.errors import UVSubprocessFailedError
from usethis._backend.uv.sync import sync_environment_via_uv
from usethis._config import usethis_config
from usethis._subprocess import SubprocessFailedError, SubprocessResult


class TestSyncEnvironmentViaUV:
    def test_groups(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        # Arrange
        calls = _mock_subprocess(monkeypatch)

        # Act
        sync_environment_via_uv(["dev", "test"], path=tmp_path)

        # Assert
        # Inexact, so that other packages aren't removed, and with the groups explicitly,
        # since they aren't necessarily installed by default
        assert [call for call, _ in calls] == [
            [
                "uv",
                "sync",
                "--no-progress",
                "--group",
                "dev",
                "--group",
                "test",
                "--inexact",
            ]
        ]

    def test_offline(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        # Arrange
        calls = _mock_subprocess(monkeypatch)

        # Act
        with usethis_config.set(offline=True):
            sync_environment_via_uv(["dev"], path=tmp_path)

        # Assert
        assert [call for call, _ in calls] == [
            [
                "uv",
                "sync",
                "--no-progress",
                "--offline",
                "--group",
                "dev",
                "--inexact",
            ]
        ]

    def test_in_given_project(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        # Arrange
        calls = _mock_subprocess(monkeypatch)
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        # Act
        sync_environment_via_uv(["dev"], path=project_dir)

        # Assert
        assert [cwd for _, cwd in calls] == [project_dir]

    def test_failure(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        # Arrange
        _mock_subprocess(monkeypatch, fail=True)

        # Act, Assert
        # It's the sync that failed, rather than anything to do with a dependency group
        with pytest.raises(UVSubprocessFailedError, match="boom"):
            sync_environment_via_uv(["dev"], path=tmp_path)


def _mock_subprocess(
    monkeypatch: pytest.MonkeyPatch, *, fail: bool = False
) -> list[tuple[list[str], Path | None]]:
    """Replace subprocess calls with a mock, returning the list of recorded calls.

    Args:
        monkeypatch: The pytest monkeypatch fixture.
        fail: Whether the mocked calls should fail.

    Returns:
        The arguments and working directory of each call.
    """
    calls: list[tuple[list[str], Path | None]] = []

    def mock_call_subprocess(
        args: list[str], *, cwd: Path | None = None
    ) -> SubprocessResult:
        calls.append((args, cwd))
        if fail:
            msg = "boom"
            raise SubprocessFailedError(msg)
        return SubprocessResult("", "")

    monkeypatch.setattr(
        usethis._backend.uv.call, "call_subprocess", mock_call_subprocess
    )
    return calls
