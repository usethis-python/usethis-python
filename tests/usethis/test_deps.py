from pathlib import Path

import pytest
from packaging.requirements import InvalidRequirement
from pydantic import TypeAdapter

import usethis._backend.uv.deps
from _test import change_cwd
from usethis._backend.uv.errors import (
    UVDepGroupError,
    UVSubprocessFailedError,
)
from usethis._config import usethis_config
from usethis._config_file import files_manager
from usethis._deps import (
    add_default_groups,
    add_deps_to_group,
    get_default_groups,
    get_dep_groups,
    get_deps_from_group,
    get_project_deps,
    is_dep_in_any_group,
    is_dep_satisfied_in,
    register_default_group,
    remove_deps_from_group,
)
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._types.backend import BackendEnum
from usethis._types.deps import Dependency
from usethis.errors import DepGroupError


class TestGetProjectDeps:
    def test_no_pyproject_toml(self, tmp_path: Path):
        # Arrange - No pyproject.toml file exists

        # Act
        with change_cwd(tmp_path), files_manager():
            result = get_project_deps()

        # Assert
        assert result == []

    def test_empty_pyproject(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").touch()

        # Act
        with change_cwd(tmp_path), files_manager():
            result = get_project_deps()

        # Assert
        assert result == []

    def test_no_project_section(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("""\
[build-system]
requires = ["setuptools"]
""")

        # Act
        with change_cwd(tmp_path), files_manager():
            result = get_project_deps()

        # Assert
        assert result == []

    def test_invalid_project_section(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("""\
project = "not a table but a string"
""")

        # Act
        with change_cwd(tmp_path), files_manager():
            result = get_project_deps()

        # Assert
        assert result == []

    def test_no_dependencies_section(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("""\
[project]
name = "test-project"
version = "0.1.0"
""")

        # Act
        with change_cwd(tmp_path), files_manager():
            result = get_project_deps()

        # Assert
        assert result == []

    def test_empty_dependencies_section(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("""\
[project]
name = "test-project"
version = "0.1.0"
dependencies = []
""")

        # Act
        with change_cwd(tmp_path), files_manager():
            result = get_project_deps()

        # Assert
        assert result == []

    def test_single_dependency(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("""\
[project]
name = "test-project"
version = "0.1.0"
dependencies = ["requests"]
""")

        # Act
        with change_cwd(tmp_path), files_manager():
            result = get_project_deps()

        # Assert
        assert result == [Dependency(name="requests")]

    def test_multiple_dependencies(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("""\
[project]
name = "test-project"
version = "0.1.0"
dependencies = ["requests", "click", "pydantic"]
""")

        # Act
        with change_cwd(tmp_path), files_manager():
            result = get_project_deps()

        # Assert
        assert result == [
            Dependency(name="requests"),
            Dependency(name="click"),
            Dependency(name="pydantic"),
        ]

    def test_dependency_with_extras(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("""\
[project]
name = "test-project"
version = "0.1.0"
dependencies = ["pydantic[email]"]
""")

        # Act
        with change_cwd(tmp_path), files_manager():
            result = get_project_deps()

        # Assert
        assert result == [Dependency(name="pydantic", extras=frozenset({"email"}))]

    def test_dependency_with_multiple_extras(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("""\
[project]
name = "test-project"
version = "0.1.0"
dependencies = ["pydantic[email,dotenv]"]
""")

        # Act
        with change_cwd(tmp_path), files_manager():
            result = get_project_deps()

        # Assert
        assert result == [
            Dependency(name="pydantic", extras=frozenset({"email", "dotenv"}))
        ]

    def test_mixed_dependencies_with_and_without_extras(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("""\
[project]
name = "test-project"
version = "0.1.0"
dependencies = ["requests", "pydantic[email]", "click"]
""")

        # Act
        with change_cwd(tmp_path), files_manager():
            result = get_project_deps()

        # Assert
        assert result == [
            Dependency(name="requests"),
            Dependency(name="pydantic", extras=frozenset({"email"})),
            Dependency(name="click"),
        ]

    def test_dependency_with_version_constraint(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("""\
[project]
name = "test-project"
version = "0.1.0"
dependencies = ["requests>=2.28.0", "click~=8.0"]
""")

        # Act
        with change_cwd(tmp_path), files_manager():
            result = get_project_deps()

        # Assert
        assert result == [
            Dependency(name="requests"),
            Dependency(name="click"),
        ]

    def test_invalid_dependencies_section_not_list(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("""\
[project]
name = "test-project"
version = "0.1.0"
dependencies = "not a list"
""")

        # Act, Assert
        with (
            change_cwd(tmp_path),
            files_manager(),
            pytest.raises(
                UVDepGroupError,
                match=r"Failed to parse the 'project.dependencies' section",
            ),
        ):
            get_project_deps()

    def test_invalid_dependencies_section_invalid_requirement(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("""\
[project]
name = "test-project"
version = "0.1.0"
dependencies = ["invalid requirement string !!!"]
""")

        # Act, Assert
        with (
            change_cwd(tmp_path),
            files_manager(),
            pytest.raises(InvalidRequirement),
        ):
            get_project_deps()

    def test_ignores_optional_dependency_groups_and_build_deps(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("""\
[build-system]
requires = ["setuptools>=45", "wheel", "build-dep"]
build-backend = "setuptools.build_meta"

[project]
name = "test-project"
version = "0.1.0"
dependencies = ["requests", "click"]

[project.optional-dependencies]
dev = ["pytest", "black"]
docs = ["sphinx", "mkdocs"]
extra = ["optional-package"]

[dependency-groups]
test = ["pytest-cov", "pytest-mock"]
qa = ["flake8", "mypy"]
lint = ["ruff"]

[tool.uv]
dev-dependencies = ["old-style-dev-dep"]
""")

        # Act
        with change_cwd(tmp_path), files_manager():
            result = get_project_deps()

        # Assert
        # Should only return the core project dependencies, ignoring:
        # - build-system.requires (build dependencies)
        # - project.optional-dependencies (optional dependencies)
        # - dependency-groups (development dependency groups)
        # - tool.uv.dev-dependencies (old-style dev dependencies)
        assert result == [
            Dependency(name="requests"),
            Dependency(name="click"),
        ]

    class TestPoetry:
        def test_legacy_poetry_deps(self, tmp_path: Path):
            """Read from [tool.poetry.dependencies] when poetry backend is active."""
            (tmp_path / "pyproject.toml").write_text("""\
[tool.poetry.dependencies]
python = "^3.10"
requests = "^2.28"
click = {version = "^8.0", extras = ["testing"]}

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
""")

            with (
                change_cwd(tmp_path),
                files_manager(),
            ):
                usethis_config.backend = BackendEnum.poetry
                result = get_project_deps()

            assert Dependency(name="requests") in result
            assert Dependency(name="click", extras=frozenset(["testing"])) in result
            # python should be excluded
            assert all(d.name != "python" for d in result)

        def test_merged_with_pep621(self, tmp_path: Path):
            """Poetry deps merge with standard [project.dependencies]."""
            (tmp_path / "pyproject.toml").write_text("""\
[project]
name = "test"
version = "0.1.0"
dependencies = ["numpy"]

[tool.poetry.dependencies]
requests = "^2.28"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
""")

            with (
                change_cwd(tmp_path),
                files_manager(),
            ):
                usethis_config.backend = BackendEnum.poetry
                result = get_project_deps()

            names = [d.name for d in result]
            assert "numpy" in names
            assert "requests" in names

        def test_no_duplicates_on_merge(self, tmp_path: Path):
            """Deps in both sections should not be duplicated."""
            (tmp_path / "pyproject.toml").write_text("""\
[project]
name = "test"
version = "0.1.0"
dependencies = ["requests>=2.0"]

[tool.poetry.dependencies]
requests = "^2.28"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
""")

            with (
                change_cwd(tmp_path),
                files_manager(),
            ):
                usethis_config.backend = BackendEnum.poetry
                result = get_project_deps()

            names = [d.name for d in result]
            assert names.count("requests") == 1


class TestGetDepGroups:
    def test_no_dev_section(self, tmp_path: Path):
        (tmp_path / "pyproject.toml").touch()

        with change_cwd(tmp_path), files_manager():
            assert get_dep_groups() == {}

    def test_empty_section(self, tmp_path: Path):
        (tmp_path / "pyproject.toml").write_text("""\
[dependency-groups]
""")

        with change_cwd(tmp_path), files_manager():
            assert get_dep_groups() == {}

    def test_empty_group(self, tmp_path: Path):
        (tmp_path / "pyproject.toml").write_text("""\
[dependency-groups]
test=[]
""")

        with change_cwd(tmp_path), files_manager():
            assert get_dep_groups() == {"test": []}

    def test_single_dev_dep(self, tmp_path: Path):
        (tmp_path / "pyproject.toml").write_text("""\
[dependency-groups]
test=['pytest']
""")

        with change_cwd(tmp_path), files_manager():
            assert get_dep_groups() == {"test": [Dependency(name="pytest")]}

    def test_multiple_dev_deps(self, tmp_path: Path):
        (tmp_path / "pyproject.toml").write_text("""\
[dependency-groups]
qa=["flake8", "black", "isort"]
""")

        with change_cwd(tmp_path), files_manager():
            assert get_dep_groups() == {
                "qa": [
                    Dependency(name="flake8"),
                    Dependency(name="black"),
                    Dependency(name="isort"),
                ]
            }

    def test_multiple_groups(self, tmp_path: Path):
        (tmp_path / "pyproject.toml").write_text(
            """\
[dependency-groups]
qa=["flake8", "black", "isort"]
test=['pytest']
"""
        )

        with change_cwd(tmp_path), files_manager():
            assert get_dep_groups() == {
                "qa": [
                    Dependency(name="flake8"),
                    Dependency(name="black"),
                    Dependency(name="isort"),
                ],
                "test": [
                    Dependency(name="pytest"),
                ],
            }

    def test_no_pyproject_toml(self, tmp_path: Path):
        # Act
        with change_cwd(tmp_path), files_manager():
            result = get_dep_groups()

        # Assert
        assert result == {}

    def test_invalid_dtype(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("""\
[dependency-groups]
test="not a list"
""")
        # Act, Assert
        with (
            change_cwd(tmp_path),
            files_manager(),
            pytest.raises(DepGroupError),
        ):
            get_dep_groups()

    class TestPoetry:
        def test_legacy_poetry_groups(self, tmp_path: Path):
            """Read from [tool.poetry.group.*.dependencies]."""
            (tmp_path / "pyproject.toml").write_text("""\
[tool.poetry.group.dev.dependencies]
pytest = "^7.0"
ruff = "^0.1"

[tool.poetry.group.docs.dependencies]
mkdocs = "^1.5"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
""")

            with (
                change_cwd(tmp_path),
                files_manager(),
            ):
                usethis_config.backend = BackendEnum.poetry
                result = get_dep_groups()

            assert "dev" in result
            assert Dependency(name="pytest") in result["dev"]
            assert Dependency(name="ruff") in result["dev"]
            assert "docs" in result
            assert Dependency(name="mkdocs") in result["docs"]

        def test_merged_with_pep735(self, tmp_path: Path):
            """Poetry groups merge with standard [dependency-groups]."""
            (tmp_path / "pyproject.toml").write_text("""\
[dependency-groups]
dev = ["pytest>=7.0"]

[tool.poetry.group.lint.dependencies]
ruff = "^0.1"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
""")

            with (
                change_cwd(tmp_path),
                files_manager(),
            ):
                usethis_config.backend = BackendEnum.poetry
                result = get_dep_groups()

            assert Dependency(name="pytest") in result["dev"]
            assert Dependency(name="ruff") in result["lint"]

        def test_same_group_merges(self, tmp_path: Path):
            """Deps from both sections for the same group are merged."""
            (tmp_path / "pyproject.toml").write_text("""\
[dependency-groups]
dev = ["pytest>=7.0"]

[tool.poetry.group.dev.dependencies]
ruff = "^0.1"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
""")

            with (
                change_cwd(tmp_path),
                files_manager(),
            ):
                usethis_config.backend = BackendEnum.poetry
                result = get_dep_groups()

            assert Dependency(name="pytest") in result["dev"]
            assert Dependency(name="ruff") in result["dev"]

        def test_no_duplicate_on_overlap(self, tmp_path: Path):
            """Same dep in both sections should not be duplicated."""
            (tmp_path / "pyproject.toml").write_text("""\
[dependency-groups]
dev = ["pytest>=7.0"]

[tool.poetry.group.dev.dependencies]
pytest = "^7.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
""")

            with (
                change_cwd(tmp_path),
                files_manager(),
            ):
                usethis_config.backend = BackendEnum.poetry
                result = get_dep_groups()

            names = [d.name for d in result["dev"]]
            assert names.count("pytest") == 1

        def test_extras_in_poetry_format(self, tmp_path: Path):
            """Poetry dict format with extras is parsed correctly."""
            (tmp_path / "pyproject.toml").write_text("""\
[tool.poetry.group.dev.dependencies]
requests = {version = "^2.28", extras = ["security", "socks"]}

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
""")

            with (
                change_cwd(tmp_path),
                files_manager(),
            ):
                usethis_config.backend = BackendEnum.poetry
                result = get_dep_groups()

            dep = result["dev"][0]
            assert dep.name == "requests"
            assert dep.extras == frozenset(["security", "socks"])

        def test_not_read_without_poetry_backend(self, tmp_path: Path):
            """Poetry sections are not read when backend is not poetry."""
            (tmp_path / "pyproject.toml").write_text("""\
[tool.poetry.group.dev.dependencies]
pytest = "^7.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
""")

            with (
                change_cwd(tmp_path),
                files_manager(),
            ):
                usethis_config.backend = BackendEnum.none
                result = get_dep_groups()

            assert result == {}


class TestAddDepsToGroup:
    @pytest.mark.usefixtures("_vary_network_conn")
    def test_pyproject_changed(self, uv_init_dir: Path):
        with change_cwd(uv_init_dir), files_manager():
            # Act
            add_deps_to_group([Dependency(name="pytest")], "test")

            # Assert
            assert is_dep_satisfied_in(
                Dependency(name="pytest"), in_=get_deps_from_group("test")
            )

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_single_dep(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
        with change_cwd(uv_init_dir), files_manager():
            # Act
            add_deps_to_group([Dependency(name="pytest")], "test")

            # Assert
            assert get_deps_from_group("test") == [Dependency(name="pytest")]
            out, err = capfd.readouterr()
            assert not err
            assert (
                out
                == "✔ Adding dependency 'pytest' to the 'test' group in 'pyproject.toml'.\n"
                "☐ Install the dependency 'pytest'.\n"
            )

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_multiple_deps(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
        with change_cwd(uv_init_dir), files_manager():
            # Act
            add_deps_to_group(
                [Dependency(name="flake8"), Dependency(name="black")], "qa"
            )

            # Assert
            assert set(get_deps_from_group("qa")) == {
                Dependency(name="flake8"),
                Dependency(name="black"),
            }
            out, err = capfd.readouterr()
            assert not err
            assert (
                out
                == "✔ Adding dependencies 'flake8', 'black' to the 'qa' group in 'pyproject.toml'.\n"
                "☐ Install the dependencies 'flake8', 'black'.\n"
            )

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_multi_but_one_already_exists(
        self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]
    ):
        with change_cwd(uv_init_dir), files_manager():
            # Arrange
            with usethis_config.set(quiet=True):
                add_deps_to_group([Dependency(name="pytest")], "test")

            # Act
            add_deps_to_group(
                [Dependency(name="pytest"), Dependency(name="black")], "test"
            )

            # Assert
            assert set(get_deps_from_group("test")) == {
                Dependency(name="pytest"),
                Dependency(name="black"),
            }
            out, err = capfd.readouterr()
            assert not err
            assert (
                out
                == "✔ Adding dependency 'black' to the 'test' group in 'pyproject.toml'.\n"
                "☐ Install the dependency 'black'.\n"
            )

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_extras(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
        with change_cwd(uv_init_dir), files_manager():
            # Act
            add_deps_to_group(
                [Dependency(name="pytest", extras=frozenset({"extra"}))], "test"
            )

            # Assert
            assert is_dep_satisfied_in(
                Dependency(name="pytest", extras=frozenset({"extra"})),
                in_=get_deps_from_group("test"),
            )
            content = (uv_init_dir / "pyproject.toml").read_text()
            assert "pytest[extra]" in content
            out, err = capfd.readouterr()
            assert not err
            assert (
                out
                == "✔ Adding dependency 'pytest' to the 'test' group in 'pyproject.toml'.\n"
                "☐ Install the dependency 'pytest'.\n"
            )

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_empty_deps(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
        with change_cwd(uv_init_dir), files_manager():
            # Act
            add_deps_to_group([], "test")

            # Assert
            assert not get_deps_from_group("test")
            out, err = capfd.readouterr()
            assert not err
            assert not out

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_extra_when_nonextra_already_present(self, uv_init_dir: Path):
        # https://github.com/usethis-python/usethis-python/issues/227
        with change_cwd(uv_init_dir), files_manager():
            # Arrange
            add_deps_to_group([Dependency(name="coverage")], "test")

            # Act
            add_deps_to_group(
                [Dependency(name="coverage", extras=frozenset({"toml"}))], "test"
            )

            # Assert
            content = (uv_init_dir / "pyproject.toml").read_text()
            assert "coverage[toml]" in content

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_extras_combining_together(self, uv_init_dir: Path):
        with change_cwd(uv_init_dir), files_manager():
            # Arrange
            add_deps_to_group(
                [Dependency(name="coverage", extras=frozenset({"toml"}))], "test"
            )

            # Act
            add_deps_to_group(
                [Dependency(name="coverage", extras=frozenset({"extra"}))], "test"
            )

            # Assert
            content = (uv_init_dir / "pyproject.toml").read_text()
            assert "coverage[extra,toml]" in content

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_combine_extras_alphabetical(self, uv_init_dir: Path):
        with change_cwd(uv_init_dir), files_manager():
            # Arrange
            add_deps_to_group(
                [Dependency(name="coverage", extras=frozenset({"extra"}))], "test"
            )

            # Act
            add_deps_to_group(
                [Dependency(name="coverage", extras=frozenset({"toml"}))], "test"
            )

            # Assert
            content = (uv_init_dir / "pyproject.toml").read_text()
            assert "coverage[extra,toml]" in content

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_registers_default_group(self, uv_init_dir: Path):
        with change_cwd(uv_init_dir), files_manager():
            # Act
            add_deps_to_group([Dependency(name="pytest")], "test")

            # Assert
            default_groups = TypeAdapter(list[str]).validate_python(
                PyprojectTOMLManager()[["tool", "uv", "default-groups"]]
            )
            assert "test" in default_groups

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_dev_group_not_registered(self, uv_init_dir: Path):
        with change_cwd(uv_init_dir), files_manager():
            # Act
            add_deps_to_group([Dependency(name="black")], "dev")

            # Assert
            assert ["tool", "uv", "default-groups"] not in PyprojectTOMLManager()

    def test_uv_subprocess_error(
        self, uv_init_dir: Path, monkeypatch: pytest.MonkeyPatch
    ):
        def mock_call_uv_subprocess(*_: object, **__: object):
            raise UVSubprocessFailedError

        monkeypatch.setattr(
            usethis._backend.uv.deps,
            "call_uv_subprocess",
            mock_call_uv_subprocess,
        )

        # Act, Assert
        with change_cwd(uv_init_dir), files_manager():
            with pytest.raises(
                DepGroupError,
                match="Failed to add 'pytest' to the 'test' dependency group",
            ):
                add_deps_to_group([Dependency(name="pytest")], "test")

            # Assert contd
            # We want to check that registration hasn't taken place
            default_groups = get_default_groups()
            assert "test" not in default_groups

    def test_none_backend(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("""\
[dependency-groups]
test = []
""")

        # Act
        with (
            usethis_config.set(backend=BackendEnum.none),
            change_cwd(tmp_path),
            files_manager(),
        ):
            add_deps_to_group([Dependency(name="pytest")], "test")

        # Assert
        out, err = capfd.readouterr()
        assert not err
        assert out == "☐ Add the test dependency 'pytest'.\n"

    def test_no_pyproject_toml(self, tmp_path: Path):
        # Act
        with change_cwd(tmp_path), files_manager():
            add_deps_to_group([Dependency(name="pytest")], "test")

            # Assert
            assert get_deps_from_group("test") == [Dependency(name="pytest")]

        content = (tmp_path / "pyproject.toml").read_text()
        assert "[dependency-groups]" in content

    class TestPoetry:
        def test_add(
            self,
            tmp_path: Path,
            capfd: pytest.CaptureFixture[str],
            monkeypatch: pytest.MonkeyPatch,
        ):
            # Arrange
            (tmp_path / "pyproject.toml").write_text("""\
[dependency-groups]
test = []
""")

            calls: list[tuple[str, str]] = []

            def mock_add_dep(dep: object, group: str) -> None:
                calls.append((str(dep), group))

            monkeypatch.setattr(
                "usethis._deps.add_dep_to_group_via_poetry",
                mock_add_dep,
            )

            with (
                usethis_config.set(backend=BackendEnum.poetry),
                change_cwd(tmp_path),
                files_manager(),
            ):
                add_deps_to_group([Dependency(name="pytest")], "test")

            out, err = capfd.readouterr()
            assert not err
            assert (
                "Adding dependency 'pytest' to the 'test' group in 'pyproject.toml'"
                in out
            )
            assert len(calls) == 1

        def test_no_default_group_registration(
            self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
        ):
            # Poetry doesn't need to register default groups
            (tmp_path / "pyproject.toml").write_text("""\
[dependency-groups]
test = []
""")

            def mock_add_dep(dep: object, group: str) -> None:
                _ = dep
                _ = group

            monkeypatch.setattr(
                "usethis._deps.add_dep_to_group_via_poetry",
                mock_add_dep,
            )

            with (
                usethis_config.set(backend=BackendEnum.poetry),
                change_cwd(tmp_path),
                files_manager(),
            ):
                add_deps_to_group([Dependency(name="pytest")], "test")

            # No uv.toml default-groups should be created
            assert not (tmp_path / "uv.toml").exists()

        def test_frozen_still_calls_add(
            self,
            tmp_path: Path,
            capfd: pytest.CaptureFixture[str],
            monkeypatch: pytest.MonkeyPatch,
        ):
            """When frozen=True, poetry deps are still declared in pyproject.toml."""
            # Arrange
            (tmp_path / "pyproject.toml").write_text("""\
[dependency-groups]
test = []
""")

            calls: list[tuple[str, str]] = []

            def mock_add_dep(dep: object, group: str) -> None:
                calls.append((str(dep), group))

            monkeypatch.setattr(
                "usethis._deps.add_dep_to_group_via_poetry",
                mock_add_dep,
            )

            with (
                usethis_config.set(backend=BackendEnum.poetry, frozen=True),
                change_cwd(tmp_path),
                files_manager(),
            ):
                add_deps_to_group([Dependency(name="pytest")], "test")

            out, err = capfd.readouterr()
            assert not err
            assert (
                "Adding dependency 'pytest' to the 'test' group in 'pyproject.toml'"
                in out
            )
            assert "Install the dependency 'pytest'" in out
            assert len(calls) == 1


class TestRemoveDepsFromGroup:
    @pytest.mark.usefixtures("_vary_network_conn")
    def test_pyproject_changed(self, uv_init_dir: Path):
        with change_cwd(uv_init_dir), files_manager():
            # Arrange
            add_deps_to_group([Dependency(name="pytest")], "test")

            # Act
            remove_deps_from_group([Dependency(name="pytest")], "test")

            # Assert
            assert "pytest" not in get_deps_from_group("test")

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_single_dep(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
        with change_cwd(uv_init_dir), files_manager():
            # Arrange
            with usethis_config.set(quiet=True):
                add_deps_to_group([Dependency(name="pytest")], "test")

            # Act
            remove_deps_from_group([Dependency(name="pytest")], "test")

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
        with change_cwd(uv_init_dir), files_manager():
            # Arrange
            with usethis_config.set(quiet=True):
                add_deps_to_group(
                    [Dependency(name="flake8"), Dependency(name="black")], "qa"
                )

            # Act
            remove_deps_from_group(
                [Dependency(name="flake8"), Dependency(name="black")], "qa"
            )

            # Assert
            assert not get_deps_from_group("qa")
            out, err = capfd.readouterr()
            assert not err
            assert (
                out
                == "✔ Removing dependencies 'flake8', 'black' from the 'qa' group in 'pyproject.toml'.\n"
            )

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_multi_but_only_not_exists(
        self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]
    ):
        with change_cwd(uv_init_dir), files_manager():
            # Arrange
            with usethis_config.set(quiet=True):
                add_deps_to_group([Dependency(name="pytest")], "test")

            # Act
            remove_deps_from_group(
                [Dependency(name="pytest"), Dependency(name="black")], "test"
            )

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
        with change_cwd(uv_init_dir), files_manager():
            # Arrange
            with usethis_config.set(quiet=True):
                add_deps_to_group(
                    [Dependency(name="pytest", extras=frozenset({"extra"}))], "test"
                )

            # Act
            remove_deps_from_group(
                [Dependency(name="pytest", extras=frozenset({"extra"}))], "test"
            )

            # Assert
            assert not get_deps_from_group("test")
            out, err = capfd.readouterr()
            assert not err
            assert (
                out
                == "✔ Removing dependency 'pytest' from the 'test' group in 'pyproject.toml'.\n"
            )

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_group_not_in_dependency_groups(
        self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]
    ):
        with change_cwd(uv_init_dir), files_manager():
            # Arrange
            with usethis_config.set(quiet=True):
                add_deps_to_group([Dependency(name="pytest")], "test")

            # Remove the group from dependency-groups but keep it in default-groups
            del PyprojectTOMLManager()[["dependency-groups", "test"]]

            # Act
            remove_deps_from_group([Dependency(name="pytest")], "test")

            # Assert
            assert not get_deps_from_group("test")
            out, err = capfd.readouterr()
            assert not err
            assert not out

    def test_uv_subprocess_error(
        self, uv_init_dir: Path, monkeypatch: pytest.MonkeyPatch
    ):
        with (
            change_cwd(uv_init_dir),
            files_manager(),
        ):
            # Arrange
            add_deps_to_group([Dependency(name="pytest")], "test")

            def mock_call_uv_subprocess(*_: object, **__: object):
                raise UVSubprocessFailedError

            monkeypatch.setattr(
                usethis._backend.uv.deps,
                "call_uv_subprocess",
                mock_call_uv_subprocess,
            )

            # Act
            with pytest.raises(
                DepGroupError,
                match="Failed to remove 'pytest' from the 'test' dependency group",
            ):
                remove_deps_from_group([Dependency(name="pytest")], "test")

    def test_none_backend(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("""\
[dependency-groups]
test = ["pytest"]
""")

        # Act
        with (
            usethis_config.set(backend=BackendEnum.none),
            change_cwd(tmp_path),
            files_manager(),
        ):
            remove_deps_from_group([Dependency(name="pytest")], "test")

        # Assert
        out, err = capfd.readouterr()
        assert not err
        assert out == "☐ Remove the test dependency 'pytest'.\n"

    class TestPoetry:
        def test_remove(
            self,
            tmp_path: Path,
            capfd: pytest.CaptureFixture[str],
            monkeypatch: pytest.MonkeyPatch,
        ):
            # Arrange
            (tmp_path / "pyproject.toml").write_text("""\
[dependency-groups]
test = ["pytest"]
""")

            calls: list[tuple[str, str]] = []

            def mock_remove_dep(dep: object, group: str) -> None:
                calls.append((str(dep), group))

            monkeypatch.setattr(
                "usethis._deps.remove_dep_from_group_via_poetry",
                mock_remove_dep,
            )

            with (
                usethis_config.set(backend=BackendEnum.poetry),
                change_cwd(tmp_path),
                files_manager(),
            ):
                remove_deps_from_group([Dependency(name="pytest")], "test")

            out, err = capfd.readouterr()
            assert not err
            assert (
                "Removing dependency 'pytest' from the 'test' group in 'pyproject.toml'"
                in out
            )
            assert len(calls) == 1

        def test_frozen_still_calls_remove(
            self,
            tmp_path: Path,
            capfd: pytest.CaptureFixture[str],
            monkeypatch: pytest.MonkeyPatch,
        ):
            """When frozen=True, poetry deps are still removed from pyproject.toml."""
            # Arrange
            (tmp_path / "pyproject.toml").write_text("""\
[dependency-groups]
test = ["pytest"]
""")

            calls: list[tuple[str, str]] = []

            def mock_remove_dep(dep: object, group: str) -> None:
                calls.append((str(dep), group))

            monkeypatch.setattr(
                "usethis._deps.remove_dep_from_group_via_poetry",
                mock_remove_dep,
            )

            with (
                usethis_config.set(backend=BackendEnum.poetry, frozen=True),
                change_cwd(tmp_path),
                files_manager(),
            ):
                remove_deps_from_group([Dependency(name="pytest")], "test")

            out, err = capfd.readouterr()
            assert not err
            assert (
                "Removing dependency 'pytest' from the 'test' group in 'pyproject.toml'"
                in out
            )
            assert len(calls) == 1


class TestIsDepInAnyGroup:
    def test_no_group(self, uv_init_dir: Path):
        with change_cwd(uv_init_dir), files_manager():
            assert not is_dep_in_any_group(Dependency(name="pytest"))

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_in_group(self, uv_init_dir: Path):
        # Arrange
        with change_cwd(uv_init_dir), files_manager():
            add_deps_to_group([Dependency(name="pytest")], "test")

            # Act
            result = is_dep_in_any_group(Dependency(name="pytest"))

        # Assert
        assert result

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_not_in_group(self, uv_init_dir: Path):
        # Arrange
        with change_cwd(uv_init_dir), files_manager():
            add_deps_to_group([Dependency(name="pytest")], "test")

            # Act
            result = is_dep_in_any_group(Dependency(name="black"))

        # Assert
        assert not result

    class TestPoetry:
        def test_in_poetry_group(self, tmp_path: Path):
            """Detect dep in [tool.poetry.group.*.dependencies]."""
            (tmp_path / "pyproject.toml").write_text("""\
[tool.poetry.group.dev.dependencies]
pytest = "^7.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
""")

            with (
                change_cwd(tmp_path),
                files_manager(),
            ):
                usethis_config.backend = BackendEnum.poetry
                assert is_dep_in_any_group(Dependency(name="pytest"))

        def test_not_in_poetry_group(self, tmp_path: Path):
            """Dep not present should return False."""
            (tmp_path / "pyproject.toml").write_text("""\
[tool.poetry.group.dev.dependencies]
pytest = "^7.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
""")

            with (
                change_cwd(tmp_path),
                files_manager(),
            ):
                usethis_config.backend = BackendEnum.poetry
                assert not is_dep_in_any_group(Dependency(name="ruff"))


class TestIsDepSatisfiedIn:
    def test_empty(self):
        # Arrange
        dep = Dependency(name="pytest")
        in_: list[Dependency] = []

        # Act
        result = is_dep_satisfied_in(dep, in_=in_)

        # Assert
        assert not result

    def test_same(self):
        # Arrange
        dep = Dependency(name="pytest")
        in_ = [Dependency(name="pytest")]

        # Act
        result = is_dep_satisfied_in(dep, in_=in_)

        # Assert
        assert result

    def test_same_name_superset_extra(self):
        # Arrange
        dep = Dependency(name="pytest", extras=frozenset({"extra"}))
        in_ = [Dependency(name="pytest")]

        # Act
        result = is_dep_satisfied_in(dep, in_=in_)

        # Assert
        assert not result

    def test_same_name_subset_extra(self):
        # Arrange
        dep = Dependency(name="pytest")
        in_ = [Dependency(name="pytest", extras=frozenset({"extra"}))]

        # Act
        result = is_dep_satisfied_in(dep, in_=in_)

        # Assert
        assert result

    def test_multiple(self):
        # Arrange
        dep = Dependency(name="pytest")
        in_ = [Dependency(name="flake8"), Dependency(name="pytest")]

        # Act
        result = is_dep_satisfied_in(dep, in_=in_)

        # Assert
        assert result


class TestRegisterDefaultGroup:
    def test_section_not_exists_adds_dev(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("")

        with (
            change_cwd(tmp_path),
            files_manager(),
            usethis_config.set(backend=BackendEnum.uv),
        ):
            # Act
            register_default_group("test")

            # Assert
            default_groups = TypeAdapter(list[str]).validate_python(
                PyprojectTOMLManager()[["tool", "uv", "default-groups"]]
            )
            assert set(default_groups) == {"test", "dev"}

    def test_empty_section_adds_dev(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("""\
[tool.uv]
""")

        with change_cwd(tmp_path), files_manager():
            # Act
            register_default_group("test")

            # Assert
            default_groups = TypeAdapter(list[str]).validate_python(
                PyprojectTOMLManager()[["tool", "uv", "default-groups"]]
            )
            assert set(default_groups) == {"test", "dev"}

    def test_empty_default_groups_adds_dev(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("""\
[tool.uv]
default-groups = []
""")

        with change_cwd(tmp_path), files_manager():
            # Act
            register_default_group("test")

            # Assert
            default_groups = TypeAdapter(list[str]).validate_python(
                PyprojectTOMLManager()[["tool", "uv", "default-groups"]]
            )
            assert set(default_groups) == {"test", "dev"}

    def test_existing_section_no_dev_added_if_no_other_groups(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("""\
[tool.uv]
default-groups = ["test"]
""")

        with change_cwd(tmp_path), files_manager():
            # Act
            register_default_group("test")

            # Assert
            default_groups = TypeAdapter(list[str]).validate_python(
                PyprojectTOMLManager()[["tool", "uv", "default-groups"]]
            )
            assert set(default_groups) == {"test"}

    def test_existing_section_no_dev_added_if_dev_exists(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("""\
[tool.uv]
default-groups = ["test", "dev"]
""")

        with change_cwd(tmp_path), files_manager():
            # Act
            register_default_group("docs")

            # Assert
            default_groups = TypeAdapter(list[str]).validate_python(
                PyprojectTOMLManager()[["tool", "uv", "default-groups"]]
            )
            assert set(default_groups) == {"test", "dev", "docs"}

    def test_existing_section_adds_dev_with_new_group(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("""\
[tool.uv]
default-groups = ["test"]
""")

        with change_cwd(tmp_path), files_manager():
            # Act
            register_default_group("docs")

            # Assert
            default_groups = TypeAdapter(list[str]).validate_python(
                PyprojectTOMLManager()[["tool", "uv", "default-groups"]]
            )
            assert set(default_groups) == {"test", "docs", "dev"}

    def test_dev_not_added_if_missing(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("""\
[tool.uv]
default-groups = ["test"]
""")

        with change_cwd(tmp_path), files_manager():
            # Act
            register_default_group("test")

            # Assert
            default_groups = TypeAdapter(list[str]).validate_python(
                PyprojectTOMLManager()[["tool", "uv", "default-groups"]]
            )
            assert set(default_groups) == {"test"}


class TestAddDefaultGroups:
    def test_uv_toml(self, tmp_path: Path):
        # Arrange
        (tmp_path / "uv.toml").touch()

        # Act
        with change_cwd(tmp_path), files_manager():
            add_default_groups(["test"])

        # Assert
        with change_cwd(tmp_path), files_manager():
            assert (
                (tmp_path / "uv.toml").read_text()
                == """\
default-groups = ["test"]
"""
            )

    def test_none_backend(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
        # N.B. should have no effect - default groups are not really defined if we
        # use the 'none' backend.
        with usethis_config.set(backend=BackendEnum.none):
            # Act
            with change_cwd(tmp_path), files_manager():
                add_default_groups(["test"])

            # Assert
            assert not (tmp_path / "uv.toml").exists()
            assert not (tmp_path / "pyproject.toml").exists()

            out, err = capfd.readouterr()
            assert not err
            assert not out

    class TestPoetry:
        def test_no_optional(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
            # When the group doesn't have optional=true, nothing changes
            (tmp_path / "pyproject.toml").write_text("""\
[dependency-groups]
test = ["pytest"]
""")
            with (
                usethis_config.set(backend=BackendEnum.poetry),
                change_cwd(tmp_path),
                files_manager(),
            ):
                add_default_groups(["test"])

            # No uv.toml should be created
            assert not (tmp_path / "uv.toml").exists()

            out, err = capfd.readouterr()
            assert not err
            assert not out

        def test_optional_to_default(self, tmp_path: Path):
            # When the group has optional=true, it should be set to false
            (tmp_path / "pyproject.toml").write_text("""\
[dependency-groups]
test = ["pytest"]

[tool.poetry.group.test]
optional = true
""")
            with (
                usethis_config.set(backend=BackendEnum.poetry),
                change_cwd(tmp_path),
                files_manager(),
            ):
                add_default_groups(["test"])

            content = (tmp_path / "pyproject.toml").read_text()
            assert "optional = false" in content


class TestGetDefaultGroups:
    def test_empty_pyproject_toml(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").touch()

        with change_cwd(tmp_path), files_manager():
            # Act
            result = get_default_groups()

            # Assert
            assert result == []

    def test_invalid_default_groups(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("""\
[tool.uv]
default-groups = "not a list"
""")

        with change_cwd(tmp_path), files_manager():
            # Act
            result = get_default_groups()

            # Assert
            assert result == []

    def test_uv_toml(self, tmp_path: Path):
        # Arrange
        (tmp_path / "uv.toml").write_text("""\
default-groups = ["test"]
""")
        # Even if the pyproject.toml disagrees!
        (tmp_path / "pyproject.toml").write_text("""\
[tool.uv]
default-groups = ["doc"]
""")

        with change_cwd(tmp_path), files_manager():
            # Act
            result = get_default_groups()

            # Assert
            assert result == ["test"]

    def test_uv_toml_empty(self, tmp_path: Path):
        # Arrange
        (tmp_path / "uv.toml").touch()
        (tmp_path / "pyproject.toml").write_text("""\
[tool.uv]
default-groups = ["doc"]
""")

        with change_cwd(tmp_path), files_manager():
            # Act
            result = get_default_groups()

            # Assert
            assert result == []

    def test_none_backend(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("""\
[tool.uv]
default-groups = ["test"]
""")

        with usethis_config.set(backend=BackendEnum.none):
            # Act
            with change_cwd(tmp_path), files_manager():
                result = get_default_groups()

            # Assert
            assert result == []

    class TestPoetry:
        def test_all_groups_default(self, tmp_path: Path):
            (tmp_path / "pyproject.toml").write_text("""\
[dependency-groups]
test = ["pytest"]
dev = ["ruff"]
""")
            with usethis_config.set(backend=BackendEnum.poetry):
                with change_cwd(tmp_path), files_manager():
                    result = get_default_groups()

                # All groups are default by default in poetry
                assert sorted(result) == ["dev", "test"]

        def test_optional_group(self, tmp_path: Path):
            (tmp_path / "pyproject.toml").write_text("""\
[dependency-groups]
test = ["pytest"]
docs = ["mkdocs"]

[tool.poetry.group.docs]
optional = true
""")
            with usethis_config.set(backend=BackendEnum.poetry):
                with change_cwd(tmp_path), files_manager():
                    result = get_default_groups()

                # docs is optional, so only test is default
                assert result == ["test"]

        def test_no_pyproject(self, tmp_path: Path):
            with usethis_config.set(backend=BackendEnum.poetry):
                with change_cwd(tmp_path), files_manager():
                    result = get_default_groups()

                assert result == []
