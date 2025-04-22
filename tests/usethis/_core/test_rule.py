from pathlib import Path

import pytest

from usethis._config_file import files_manager
from usethis._core.rule import remove_rules, use_rules
from usethis._integrations.uv.deps import Dependency, get_deps_from_group
from usethis._test import change_cwd
from usethis._tool import RuffTool


class TestUseRules:
    def test_ruff_gets_installed(self, uv_init_dir: Path):
        with change_cwd(uv_init_dir), files_manager():
            # Act
            use_rules(rules=["A"])

            # Assert
            assert Dependency(name="ruff") in get_deps_from_group(group="dev")

    def test_deptry_gets_installed(self, uv_init_dir: Path):
        with change_cwd(uv_init_dir), files_manager():
            # Act
            use_rules(rules=["DEP001"])

            # Assert
            assert Dependency(name="deptry") in get_deps_from_group(group="dev")

    def test_success(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
        with change_cwd(uv_init_dir), files_manager():
            # Arrange
            (uv_init_dir / "ruff.toml").touch()  # avoid installation messages for ruff

            # Act
            use_rules(rules=["RUF001"])

            # Assert
            assert "RUF001" in RuffTool().get_selected_rules()

        out, err = capfd.readouterr()
        assert not err
        assert out == "✔ Enabling Ruff rule 'RUF001' in 'ruff.toml'.\n"


class TestRemoveRules:
    def test_success(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
        with change_cwd(uv_init_dir), files_manager():
            # Arrange
            (uv_init_dir / "ruff.toml").write_text(
                """\
[lint]
select = ["RUF001"]
"""
            )

            # Act
            remove_rules(rules=["RUF001"])

            # Assert
            assert "RUF001" not in RuffTool().get_selected_rules()

        out, err = capfd.readouterr()
        assert not err
        assert out == "✔ Disabling Ruff rule 'RUF001' in 'ruff.toml'.\n"
