import pytest

import usethis._backend.uv.deps
from usethis._backend.uv.deps import add_dep_to_group_via_uv
from usethis._backend.uv.errors import UVDepGroupError, UVSubprocessFailedError
from usethis._types.deps import Dependency


class TestAddDepToGroupViaUV:
    def test_syncs_by_default(self, monkeypatch: pytest.MonkeyPatch):
        # Arrange
        calls = _mock_call_uv_subprocess(monkeypatch)

        # Act
        add_dep_to_group_via_uv(Dependency(name="ruff"), "dev")

        # Assert
        assert calls == [(_ADD_RUFF, False)]

    def test_no_sync(self, monkeypatch: pytest.MonkeyPatch):
        # Arrange
        calls = _mock_call_uv_subprocess(monkeypatch)

        # Act
        add_dep_to_group_via_uv(Dependency(name="ruff"), "dev", no_sync=True)

        # Assert
        assert calls == [(_ADD_RUFF, True)]

    def test_failure(self, monkeypatch: pytest.MonkeyPatch):
        # Arrange
        calls = _mock_call_uv_subprocess(monkeypatch, fail=True)

        # Act, Assert
        with pytest.raises(
            UVDepGroupError,
            match="Failed to add 'ruff' to the 'dev' dependency group:\nboom",
        ):
            add_dep_to_group_via_uv(Dependency(name="ruff"), "dev", no_sync=True)

        assert calls == [(_ADD_RUFF, True)]


_ADD_RUFF = ["add", "--group", "dev", "ruff"]


def _mock_call_uv_subprocess(
    monkeypatch: pytest.MonkeyPatch, *, fail: bool = False
) -> list[tuple[list[str], bool]]:
    """Replace uv subprocess calls with a mock, returning the list of recorded calls.

    Args:
        monkeypatch: The pytest monkeypatch fixture.
        fail: Whether the mocked calls should fail.

    Returns:
        The arguments of each call, and whether it was told not to sync.
    """
    calls: list[tuple[list[str], bool]] = []

    def mock_call_uv_subprocess(
        args: list[str], *, change_toml: bool = True, no_sync: bool = False
    ) -> str:
        _ = change_toml
        calls.append((args, no_sync))
        if fail:
            msg = "boom"
            raise UVSubprocessFailedError(msg)
        return ""

    monkeypatch.setattr(
        usethis._backend.uv.deps, "call_uv_subprocess", mock_call_uv_subprocess
    )
    return calls
