from usethis._backend.poetry.errors import (
    PoetryDepGroupError,
    PoetryError,
    PoetryInitError,
    PoetrySubprocessFailedError,
)
from usethis.errors import DepGroupError, UsethisError


class TestPoetryErrorHierarchy:
    def test_poetry_error_is_usethis_error(self):
        assert issubclass(PoetryError, UsethisError)

    def test_subprocess_error_is_poetry_error(self):
        assert issubclass(PoetrySubprocessFailedError, PoetryError)

    def test_init_error_is_subprocess_error(self):
        assert issubclass(PoetryInitError, PoetrySubprocessFailedError)

    def test_dep_group_error_is_dep_group_error(self):
        assert issubclass(PoetryDepGroupError, DepGroupError)
