from pathlib import Path

from usethis._config import usethis_config
from usethis._file.dir import get_project_name_from_dir


class TestGetProjectNameFromDir:
    def test_simple_name(self, tmp_path: Path):
        path = tmp_path / "my_project"
        path.mkdir()
        with usethis_config.set(project_dir=path):
            assert get_project_name_from_dir() == "my_project"

    def test_leading_dot(self, tmp_path: Path):
        path = tmp_path / ".github-private"
        path.mkdir()
        with usethis_config.set(project_dir=path):
            assert get_project_name_from_dir() == "github-private"

    def test_leading_dots(self, tmp_path: Path):
        path = tmp_path / "..hidden"
        path.mkdir()
        with usethis_config.set(project_dir=path):
            assert get_project_name_from_dir() == "hidden"

    def test_trailing_dot(self, tmp_path: Path):
        path = tmp_path / "project."
        path.mkdir()
        with usethis_config.set(project_dir=path):
            assert get_project_name_from_dir() == "project"

    def test_leading_and_trailing_non_alphanumeric(self, tmp_path: Path):
        path = tmp_path / "-_project_-"
        path.mkdir()
        with usethis_config.set(project_dir=path):
            assert get_project_name_from_dir() == "project"

    def test_only_dots(self, tmp_path: Path):
        path = tmp_path / "..."
        path.mkdir()
        with usethis_config.set(project_dir=path):
            assert get_project_name_from_dir() == "hello_world"

    def test_no_valid_chars(self, tmp_path: Path):
        path = tmp_path / "+"
        path.mkdir()
        with usethis_config.set(project_dir=path):
            assert get_project_name_from_dir() == "hello_world"

    def test_drops_invalid_chars(self, tmp_path: Path):
        path = tmp_path / "h-e+l.l_o"
        path.mkdir()
        with usethis_config.set(project_dir=path):
            assert get_project_name_from_dir() == "h-el.l_o"
