from pathlib import Path

from usethis._integrations.uv.deps import get_dev_deps
from usethis._utils._test import change_cwd


class TestGetDevDeps:
    def test_no_dev_section(self, tmp_path: Path):
        (tmp_path / "pyproject.toml").touch()

        with change_cwd(tmp_path):
            assert get_dev_deps() == []

    def test_empty_dev_section(self, tmp_path: Path):
        (tmp_path / "pyproject.toml").write_text(
            "[tool.uv]\n" "dev-dependencies = []\n"
        )

        with change_cwd(tmp_path):
            assert get_dev_deps() == []

    def test_single_dev_dep(self, tmp_path: Path):
        (tmp_path / "pyproject.toml").write_text(
            "[tool.uv]\n" 'dev-dependencies = ["pytest"]\n'
        )

        with change_cwd(tmp_path):
            assert get_dev_deps() == ["pytest"]

    def test_multiple_dev_deps(self, tmp_path: Path):
        (tmp_path / "pyproject.toml").write_text(
            "[tool.uv]\n" 'dev-dependencies = ["pytest", "flake8", "black"]\n'
        )

        with change_cwd(tmp_path):
            assert get_dev_deps() == ["pytest", "flake8", "black"]
