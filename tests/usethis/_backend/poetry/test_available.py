import pytest

import usethis._backend.poetry.available
from usethis._backend.poetry.available import is_poetry_available
from usethis._backend.poetry.errors import PoetrySubprocessFailedError


class TestIsPoetryAvailable:
    def test_available_when_installed(self):
        # Poetry is a test dependency, so it should be available
        assert is_poetry_available()

    def test_mock_not_available(self, monkeypatch: pytest.MonkeyPatch):
        def mock_call_poetry_subprocess(*_: object, **__: object):
            raise PoetrySubprocessFailedError

        monkeypatch.setattr(
            usethis._backend.poetry.available,
            "call_poetry_subprocess",
            mock_call_poetry_subprocess,
        )

        result = is_poetry_available()

        assert not result
