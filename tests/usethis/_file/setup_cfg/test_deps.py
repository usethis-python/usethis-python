"""Tests for setup.cfg dependency extraction."""

from pathlib import Path

import pytest
from packaging.requirements import InvalidRequirement

from usethis._file.setup_cfg.deps import (
    get_setup_cfg_dep_groups,
    get_setup_cfg_project_deps,
)
from usethis._file.setup_cfg.io_ import SetupCFGManager
from usethis._test import change_cwd
from usethis._types.deps import Dependency


class TestGetSetupCfgProjectDeps:
    def test_no_setup_cfg(self, tmp_path: Path):
        with change_cwd(tmp_path), SetupCFGManager():
            result = get_setup_cfg_project_deps()

        assert result == []

    def test_no_options_section(self, tmp_path: Path):
        (tmp_path / "setup.cfg").write_text("[metadata]\nname = mypackage\n")

        with change_cwd(tmp_path), SetupCFGManager():
            result = get_setup_cfg_project_deps()

        assert result == []

    def test_no_install_requires(self, tmp_path: Path):
        (tmp_path / "setup.cfg").write_text("[options]\npython_requires = >=3.8\n")

        with change_cwd(tmp_path), SetupCFGManager():
            result = get_setup_cfg_project_deps()

        assert result == []

    def test_single_dependency(self, tmp_path: Path):
        (tmp_path / "setup.cfg").write_text(
            "[options]\ninstall_requires =\n    requests\n"
        )

        with change_cwd(tmp_path), SetupCFGManager():
            result = get_setup_cfg_project_deps()

        assert result == [Dependency(name="requests")]

    def test_multiple_dependencies(self, tmp_path: Path):
        (tmp_path / "setup.cfg").write_text(
            "[options]\ninstall_requires =\n    requests\n    click\n    pydantic\n"
        )

        with change_cwd(tmp_path), SetupCFGManager():
            result = get_setup_cfg_project_deps()

        assert result == [
            Dependency(name="requests"),
            Dependency(name="click"),
            Dependency(name="pydantic"),
        ]

    def test_dependency_with_version_constraint(self, tmp_path: Path):
        (tmp_path / "setup.cfg").write_text(
            "[options]\ninstall_requires =\n    requests>=2.28.0\n    click~=8.0\n"
        )

        with change_cwd(tmp_path), SetupCFGManager():
            result = get_setup_cfg_project_deps()

        assert result == [
            Dependency(name="requests"),
            Dependency(name="click"),
        ]

    def test_dependency_with_extras(self, tmp_path: Path):
        (tmp_path / "setup.cfg").write_text(
            "[options]\ninstall_requires =\n    pydantic[email]\n"
        )

        with change_cwd(tmp_path), SetupCFGManager():
            result = get_setup_cfg_project_deps()

        assert result == [Dependency(name="pydantic", extras=frozenset({"email"}))]

    def test_ignores_comment_lines(self, tmp_path: Path):
        (tmp_path / "setup.cfg").write_text(
            "[options]\ninstall_requires =\n    # a comment\n    requests\n"
        )

        with change_cwd(tmp_path), SetupCFGManager():
            result = get_setup_cfg_project_deps()

        assert result == [Dependency(name="requests")]

    def test_ignores_empty_lines(self, tmp_path: Path):
        (tmp_path / "setup.cfg").write_text(
            "[options]\ninstall_requires =\n    requests\n\n    click\n"
        )

        with change_cwd(tmp_path), SetupCFGManager():
            result = get_setup_cfg_project_deps()

        assert result == [
            Dependency(name="requests"),
            Dependency(name="click"),
        ]

    def test_invalid_requirement_raises(self, tmp_path: Path):
        (tmp_path / "setup.cfg").write_text(
            "[options]\ninstall_requires =\n    invalid requirement !!!\n"
        )

        with (
            change_cwd(tmp_path),
            SetupCFGManager(),
            pytest.raises(InvalidRequirement),
        ):
            get_setup_cfg_project_deps()


class TestGetSetupCfgDepGroups:
    def test_no_setup_cfg(self, tmp_path: Path):
        with change_cwd(tmp_path), SetupCFGManager():
            result = get_setup_cfg_dep_groups()

        assert result == {}

    def test_no_extras_require_section(self, tmp_path: Path):
        (tmp_path / "setup.cfg").write_text("[options]\npython_requires = >=3.8\n")

        with change_cwd(tmp_path), SetupCFGManager():
            result = get_setup_cfg_dep_groups()

        assert result == {}

    def test_single_group(self, tmp_path: Path):
        (tmp_path / "setup.cfg").write_text(
            "[options.extras_require]\ndev =\n    pytest\n    ruff\n"
        )

        with change_cwd(tmp_path), SetupCFGManager():
            result = get_setup_cfg_dep_groups()

        assert "dev" in result
        assert Dependency(name="pytest") in result["dev"]
        assert Dependency(name="ruff") in result["dev"]

    def test_multiple_groups(self, tmp_path: Path):
        (tmp_path / "setup.cfg").write_text(
            "[options.extras_require]\n"
            "dev =\n    pytest\n    ruff\n"
            "docs =\n    mkdocs\n"
        )

        with change_cwd(tmp_path), SetupCFGManager():
            result = get_setup_cfg_dep_groups()

        assert "dev" in result
        assert Dependency(name="pytest") in result["dev"]
        assert Dependency(name="ruff") in result["dev"]
        assert "docs" in result
        assert Dependency(name="mkdocs") in result["docs"]

    def test_group_with_version_constraints(self, tmp_path: Path):
        (tmp_path / "setup.cfg").write_text(
            "[options.extras_require]\ntest =\n    pytest>=7.0\n    coverage>=6.0\n"
        )

        with change_cwd(tmp_path), SetupCFGManager():
            result = get_setup_cfg_dep_groups()

        assert result == {
            "test": [
                Dependency(name="pytest"),
                Dependency(name="coverage"),
            ]
        }

    def test_group_with_extras(self, tmp_path: Path):
        (tmp_path / "setup.cfg").write_text(
            "[options.extras_require]\ndev =\n    pydantic[email]\n"
        )

        with change_cwd(tmp_path), SetupCFGManager():
            result = get_setup_cfg_dep_groups()

        assert result == {
            "dev": [Dependency(name="pydantic", extras=frozenset({"email"}))]
        }

    def test_empty_group_excluded(self, tmp_path: Path):
        (tmp_path / "setup.cfg").write_text(
            "[options.extras_require]\ndev =\n    pytest\nempty =\n"
        )

        with change_cwd(tmp_path), SetupCFGManager():
            result = get_setup_cfg_dep_groups()

        assert "dev" in result
        assert "empty" not in result
