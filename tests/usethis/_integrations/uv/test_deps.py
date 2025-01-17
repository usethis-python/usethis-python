from pathlib import Path

import pytest

from usethis._config import usethis_config
from usethis._integrations.uv.deps import (
    add_deps_to_group,
    get_dep_groups,
    get_deps_from_group,
    is_dep_in_any_group,
    remove_deps_from_group,
)
from usethis._integrations.uv.errors import UVDepGroupError
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
    @pytest.mark.usefixtures("_vary_network_conn")
    def test_pyproject_changed(self, uv_init_dir: Path):
        with change_cwd(uv_init_dir):
            # Act
            add_deps_to_group(["pytest"], "test")

            # Assert
            assert "pytest" in get_deps_from_group("test")

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_single_dep(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
        with change_cwd(uv_init_dir):
            # Act
            add_deps_to_group(["pytest"], "test")

            # Assert
            assert get_deps_from_group("test") == ["pytest"]
            out, err = capfd.readouterr()
            assert not err
            assert (
                out
                == "✔ Adding dependency 'pytest' to the 'test' group in 'pyproject.toml'.\n"
            )

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_multiple_deps(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
        with change_cwd(uv_init_dir):
            # Act
            add_deps_to_group(["flake8", "black"], "qa")

            # Assert
            assert set(get_deps_from_group("qa")) == {"flake8", "black"}
            out, err = capfd.readouterr()
            assert not err
            assert (
                out
                == "✔ Adding dependencies 'flake8', 'black' to the 'qa' group in 'pyproject.toml'.\n"
            )

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_multi_but_one_already_exists(
        self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]
    ):
        with change_cwd(uv_init_dir):
            # Arrange
            with usethis_config.set(quiet=True):
                add_deps_to_group(["pytest"], "test")

            # Act
            add_deps_to_group(["pytest", "black"], "test")

            # Assert
            assert set(get_deps_from_group("test")) == {"pytest", "black"}
            out, err = capfd.readouterr()
            assert not err
            assert (
                out
                == "✔ Adding dependency 'black' to the 'test' group in 'pyproject.toml'.\n"
            )

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_extras(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
        with change_cwd(uv_init_dir):
            # Act
            add_deps_to_group(["pytest[extra]"], "test")

            # Assert
            assert "pytest" in get_deps_from_group("test")
            content = (uv_init_dir / "pyproject.toml").read_text()
            assert "pytest[extra]" in content
            out, err = capfd.readouterr()
            assert not err
            assert (
                out
                == "✔ Adding dependency 'pytest' to the 'test' group in 'pyproject.toml'.\n"
            )

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_empty_deps(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
        with change_cwd(uv_init_dir):
            # Act
            add_deps_to_group([], "test")

            # Assert
            assert not get_deps_from_group("test")
            out, err = capfd.readouterr()
            assert not err
            assert not out

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_bad_dep_string(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
        with change_cwd(uv_init_dir), pytest.raises(UVDepGroupError):
            add_deps_to_group(["pytest[extra"], "test")


class TestRemoveDepsFromGroup:
    @pytest.mark.usefixtures("_vary_network_conn")
    def test_pyproject_changed(self, uv_init_dir: Path):
        with change_cwd(uv_init_dir):
            # Arrange
            add_deps_to_group(["pytest"], "test")

            # Act
            remove_deps_from_group(["pytest"], "test")

            # Assert
            assert "pytest" not in get_deps_from_group("test")

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_single_dep(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
        with change_cwd(uv_init_dir):
            # Arrange
            with usethis_config.set(quiet=True):
                add_deps_to_group(["pytest"], "test")

            # Act
            remove_deps_from_group(["pytest"], "test")

            # Assert
            assert not get_deps_from_group("test")
            out, err = capfd.readouterr()
            assert not err
            assert (
                out
                == "✔ Removing dependency 'pytest' from the 'test' group in 'pyproject.toml'.\n"
            )

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_multiple_deps(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
        with change_cwd(uv_init_dir):
            # Arrange
            with usethis_config.set(quiet=True):
                add_deps_to_group(["flake8", "black"], "qa")

            # Act
            remove_deps_from_group(["flake8", "black"], "qa")

            # Assert
            assert not get_deps_from_group("qa")
            out, err = capfd.readouterr()
            assert not err
            assert (
                out
                == "✔ Removing dependencies 'flake8', 'black' from the 'qa' group in \n'pyproject.toml'.\n"
            )

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_multi_but_only_not_exists(
        self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]
    ):
        with change_cwd(uv_init_dir):
            # Arrange
            with usethis_config.set(quiet=True):
                add_deps_to_group(["pytest"], "test")

            # Act
            remove_deps_from_group(["pytest", "black"], "test")

            # Assert
            assert not get_deps_from_group("test")
            out, err = capfd.readouterr()
            assert not err
            assert (
                out
                == "✔ Removing dependency 'pytest' from the 'test' group in 'pyproject.toml'.\n"
            )

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_extras(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
        with change_cwd(uv_init_dir):
            # Arrange
            with usethis_config.set(quiet=True):
                add_deps_to_group(["pytest[extra]"], "test")

            # Act
            remove_deps_from_group(["pytest[extra]"], "test")

            # Assert
            assert not get_deps_from_group("test")
            out, err = capfd.readouterr()
            assert not err
            assert (
                out
                == "✔ Removing dependency 'pytest' from the 'test' group in 'pyproject.toml'.\n"
            )


class TestIsDepInAnyGroup:
    def test_no_group(self, uv_init_dir: Path):
        with change_cwd(uv_init_dir):
            assert not is_dep_in_any_group("pytest")

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_in_group(self, uv_init_dir: Path):
        # Arrange
        with change_cwd(uv_init_dir):
            add_deps_to_group(["pytest"], "test")

            # Act
            result = is_dep_in_any_group("pytest")

        # Assert
        assert result

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_not_in_group(self, uv_init_dir: Path):
        # Arrange
        with change_cwd(uv_init_dir):
            add_deps_to_group(["pytest"], "test")

            # Act
            result = is_dep_in_any_group("black")

        # Assert
        assert not result
