from pathlib import Path

from usethis._integrations.uv.deps import (
    add_deps_to_group,
    get_dep_groups,
    get_deps_from_group,
    is_dep_in_any_group,
    remove_deps_from_group,
)
from usethis._test import change_cwd


class TestGetDepGroups:
    def test_no_dev_section(self, tmp_path: Path):
        (tmp_path / "pyproject.toml").touch()

        with change_cwd(tmp_path):
            assert get_dep_groups() == {}

    def test_empty_section(self, tmp_path: Path):
        (tmp_path / "pyproject.toml").write_text("""\
[dependency-groups]
""")

        with change_cwd(tmp_path):
            assert get_dep_groups() == {}

    def test_empty_group(self, tmp_path: Path):
        (tmp_path / "pyproject.toml").write_text("""\
[dependency-groups]
test=[]
""")

        with change_cwd(tmp_path):
            assert get_dep_groups() == {"test": []}

    def test_single_dev_dep(self, tmp_path: Path):
        (tmp_path / "pyproject.toml").write_text("""\
[dependency-groups]
test=['pytest']
""")

        with change_cwd(tmp_path):
            assert get_dep_groups() == {"test": ["pytest"]}

    def test_multiple_dev_deps(self, tmp_path: Path):
        (tmp_path / "pyproject.toml").write_text("""\
[dependency-groups]
qa=["flake8", "black", "isort"]
""")

        with change_cwd(tmp_path):
            assert get_dep_groups() == {"qa": ["flake8", "black", "isort"]}

    def test_multiple_groups(self, tmp_path: Path):
        (tmp_path / "pyproject.toml").write_text(
            """\
[dependency-groups]
qa=["flake8", "black", "isort"]
test=['pytest']
"""
        )

        with change_cwd(tmp_path):
            assert get_dep_groups() == {
                "qa": ["flake8", "black", "isort"],
                "test": ["pytest"],
            }


class TestAddDepsToGroup:
    def test_pyproject_changed(self, uv_init_dir: Path, vary_network_conn: None):
        with change_cwd(uv_init_dir):
            # Act
            add_deps_to_group(["pytest"], "test")

            # Assert
            assert "pytest" in get_deps_from_group("test")


class TestRemoveDepsFromGroup:
    def test_pyproject_changed(self, uv_init_dir: Path, vary_network_conn: None):
        with change_cwd(uv_init_dir):
            # Arrange
            add_deps_to_group(["pytest"], "test")

            # Act
            remove_deps_from_group(["pytest"], "test")

            # Assert
            assert "pytest" not in get_deps_from_group("test")


class TestIsDepInAnyGroup:
    def test_no_group(self, uv_init_dir: Path):
        with change_cwd(uv_init_dir):
            assert not is_dep_in_any_group("pytest")

    def test_in_group(self, uv_init_dir: Path, vary_network_conn: None):
        # Arrange
        with change_cwd(uv_init_dir):
            add_deps_to_group(["pytest"], "test")

            # Act
            result = is_dep_in_any_group("pytest")

        # Assert
        assert result

    def test_not_in_group(self, uv_init_dir: Path, vary_network_conn: None):
        # Arrange
        with change_cwd(uv_init_dir):
            add_deps_to_group(["pytest"], "test")

            # Act
            result = is_dep_in_any_group("black")

        # Assert
        assert not result
