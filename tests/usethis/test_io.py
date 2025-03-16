from pathlib import Path

from usethis._io import UsethisFileManager
from usethis._test import change_cwd


class TestUsethisFileManager:
    class TestContent:
        def test_setter(self, tmp_path: Path) -> None:
            # Arrange
            class MyUsethisFileManager(UsethisFileManager):
                @property
                def relative_path(self) -> Path:
                    return Path("pyproject.toml")

            with change_cwd(tmp_path):
                manager = MyUsethisFileManager()

            # Act
            manager._content = 42

            # Assert
            assert manager._content == 42
