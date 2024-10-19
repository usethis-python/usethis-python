from pathlib import Path

from usethis._uv.deps import get_dev_deps


class TestGetDevDeps:
    def test_no_dev_section(self, tmp_path: Path):
        (tmp_path / "pyproject.toml").touch()

        assert get_dev_deps(tmp_path) == []

    def test_empty_dev_section(self, tmp_path: Path):
        (tmp_path / "pyproject.toml").write_text(
            "[tool.uv]\n" "dev-dependencies = []\n"
        )

        assert get_dev_deps(tmp_path) == []

    def test_single_dev_dep(self, tmp_path: Path):
        (tmp_path / "pyproject.toml").write_text(
            "[tool.uv]\n" 'dev-dependencies = ["pytest"]\n'
        )

        assert get_dev_deps(tmp_path) == ["pytest"]

    def test_multiple_dev_deps(self, tmp_path: Path):
        (tmp_path / "pyproject.toml").write_text(
            "[tool.uv]\n" 'dev-dependencies = ["pytest", "flake8", "black"]\n'
        )

        assert get_dev_deps(tmp_path) == ["pytest", "flake8", "black"]
