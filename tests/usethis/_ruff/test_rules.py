from pathlib import Path

import pytest

from usethis._pyproject.io import PyProjectTOMLNotFoundError
from usethis._ruff.rules import get_ruff_rules, select_ruff_rules
from usethis._test import change_cwd


class TestSelectRuffRules:
    def test_no_pyproject_toml(self, tmp_path: Path):
        # Act
        with change_cwd(tmp_path), pytest.raises(PyProjectTOMLNotFoundError):
            select_ruff_rules(["A", "B", "C"])

    def test_blank_slate(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("")

        # Act
        new_rules = ["A", "B", "C"]
        with change_cwd(tmp_path):
            select_ruff_rules(new_rules)

            # Assert
            rules = get_ruff_rules()
        assert rules == new_rules

    def test_mixing(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """
[tool.ruff.lint]
select = ["A", "B"]
"""
        )

        # Act
        with change_cwd(tmp_path):
            select_ruff_rules(["C", "D"])

            # Assert
            rules = get_ruff_rules()
        assert rules == ["A", "B", "C", "D"]
