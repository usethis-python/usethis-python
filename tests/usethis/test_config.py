from pathlib import Path

from usethis._config import UsethisConfig
from usethis._test import change_cwd


class TestUsethisConfig:
    class TestCPD:
        def test_matches_path_cwd(self, tmp_path: Path):
            # Arrange
            config = UsethisConfig()

            # Act
            with change_cwd(tmp_path):
                cwd = config.cpd()

            # Assert
            assert cwd == tmp_path

        def test_set_overrides_cwd(self, tmp_path: Path):
            # Arrange
            config = UsethisConfig()

            # Act
            with (
                change_cwd(tmp_path),
                config.set(project_dir=Path("42 Wallaby Way, Sydney")),
            ):
                project_dir = config.cpd()

            # Assert
            assert project_dir == Path("42 Wallaby Way, Sydney")
