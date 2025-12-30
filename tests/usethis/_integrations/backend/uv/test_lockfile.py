from pathlib import Path
from typing import Any

import pytest

import usethis._integrations.backend.uv.lockfile
from usethis._integrations.backend.uv.lockfile import ensure_uv_lock
from usethis._test import change_cwd


class TestEnsureUVLock:
    def test_creates_lock_file_when_missing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[project]
name = "test"
version = "0.1.0"
dependencies = []
"""
        )

        called = False

        def mock_call_uv_subprocess(args: list[str], *, change_toml: bool) -> str:
            nonlocal called
            called = True
            assert args == ["lock"]
            assert change_toml is False
            # Create the lock file to simulate uv lock behavior
            (tmp_path / "uv.lock").write_text("version = 1\n")
            return ""

        monkeypatch.setattr(
            usethis._integrations.backend.uv.lockfile,
            "call_uv_subprocess",
            mock_call_uv_subprocess,
        )

        # Act
        with change_cwd(tmp_path):
            ensure_uv_lock()

        # Assert
        assert called
        assert (tmp_path / "uv.lock").exists()

    def test_prints_message_when_creating(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capfd: pytest.CaptureFixture[str],
    ):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[project]
name = "test"
version = "0.1.0"
dependencies = []
"""
        )

        def mock_call_uv_subprocess(args: list[str], *, change_toml: bool) -> str:
            _ = args, change_toml
            (tmp_path / "uv.lock").write_text("version = 1\n")
            return ""

        monkeypatch.setattr(
            usethis._integrations.backend.uv.lockfile,
            "call_uv_subprocess",
            mock_call_uv_subprocess,
        )

        # Act
        with change_cwd(tmp_path):
            ensure_uv_lock()

        # Assert
        out, err = capfd.readouterr()
        assert not err
        assert out == "✔ Writing 'uv.lock'.\n"

    def test_does_nothing_when_lock_exists(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capfd: pytest.CaptureFixture[str],
    ):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[project]
name = "test"
version = "0.1.0"
dependencies = []
"""
        )
        (tmp_path / "uv.lock").write_text("version = 1\n")

        called = False

        def mock_call_uv_subprocess(*_: Any, **__: Any) -> str:
            nonlocal called
            called = True
            return ""

        monkeypatch.setattr(
            usethis._integrations.backend.uv.lockfile,
            "call_uv_subprocess",
            mock_call_uv_subprocess,
        )

        # Act
        with change_cwd(tmp_path):
            ensure_uv_lock()

        # Assert
        assert not called
        out, err = capfd.readouterr()
        assert not err
        assert not out
