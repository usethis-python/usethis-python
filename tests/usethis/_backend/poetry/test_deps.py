import pytest

import usethis._backend.poetry.deps
from usethis._backend.poetry.deps import (
    add_dep_to_group_via_poetry,
    remove_dep_from_group_via_poetry,
)
from usethis._backend.poetry.errors import (
    PoetryDepGroupError,
    PoetrySubprocessFailedError,
)
from usethis._types.deps import Dependency


class TestAddDepToGroupViaPoetry:
    def test_success(self, monkeypatch: pytest.MonkeyPatch):
        captured_args: list[str] = []

        def mock_call_poetry_subprocess(
            args: list[str], *, change_toml: bool
        ) -> str:
            _ = change_toml
            captured_args.extend(args)
            return ""

        monkeypatch.setattr(
            usethis._backend.poetry.deps,
            "call_poetry_subprocess",
            mock_call_poetry_subprocess,
        )

        dep = Dependency(name="pytest")
        add_dep_to_group_via_poetry(dep, "test")

        assert captured_args == ["add", "--group", "test", "pytest"]

    def test_failure_raises_dep_group_error(self, monkeypatch: pytest.MonkeyPatch):
        def mock_call_poetry_subprocess(*_: object, **__: object) -> str:
            msg = "mock failure"
            raise PoetrySubprocessFailedError(msg)

        monkeypatch.setattr(
            usethis._backend.poetry.deps,
            "call_poetry_subprocess",
            mock_call_poetry_subprocess,
        )

        dep = Dependency(name="pytest")
        with pytest.raises(PoetryDepGroupError, match="Failed to add 'pytest'"):
            add_dep_to_group_via_poetry(dep, "test")


class TestRemoveDepFromGroupViaPoetry:
    def test_success(self, monkeypatch: pytest.MonkeyPatch):
        captured_args: list[str] = []

        def mock_call_poetry_subprocess(
            args: list[str], *, change_toml: bool
        ) -> str:
            _ = change_toml
            captured_args.extend(args)
            return ""

        monkeypatch.setattr(
            usethis._backend.poetry.deps,
            "call_poetry_subprocess",
            mock_call_poetry_subprocess,
        )

        dep = Dependency(name="pytest")
        remove_dep_from_group_via_poetry(dep, "test")

        assert captured_args == ["remove", "--group", "test", "pytest"]

    def test_failure_raises_dep_group_error(self, monkeypatch: pytest.MonkeyPatch):
        def mock_call_poetry_subprocess(*_: object, **__: object) -> str:
            msg = "mock failure"
            raise PoetrySubprocessFailedError(msg)

        monkeypatch.setattr(
            usethis._backend.poetry.deps,
            "call_poetry_subprocess",
            mock_call_poetry_subprocess,
        )

        dep = Dependency(name="pytest")
        with pytest.raises(
            PoetryDepGroupError, match="Failed to remove 'pytest'"
        ):
            remove_dep_from_group_via_poetry(dep, "test")
