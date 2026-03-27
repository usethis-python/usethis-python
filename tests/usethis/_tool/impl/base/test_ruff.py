from pathlib import Path

import pytest

from usethis._config_file import DotRuffTOMLManager, RuffTOMLManager, files_manager
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._test import change_cwd
from usethis._tool.impl.base.ruff import RuffTool


class TestRuffTool:
    class TestSelectRules:
        def test_no_pyproject_toml(
            self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
        ):
            # Act
            with (
                change_cwd(tmp_path),
                files_manager(),
            ):
                RuffTool().select_rules(["A", "B", "C"])

                # Assert
                assert RuffTool().selected_rules() == ["A", "B", "C"]

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert out == ("✔ Selecting Ruff rules 'A', 'B', 'C' in 'ruff.toml'.\n")

        def test_message(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
            # Arrange
            (tmp_path / "pyproject.toml").write_text("")

            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                RuffTool().select_rules(["A", "B", "C"])

            # Assert
            out, _ = capfd.readouterr()
            assert "✔ Selecting Ruff rules 'A', 'B', 'C' in 'pyproject.toml" in out

        def test_blank_slate(self, tmp_path: Path):
            # Arrange
            (tmp_path / "pyproject.toml").write_text("")

            # Act
            new_rules = ["A", "B", "C"]
            with change_cwd(tmp_path), PyprojectTOMLManager():
                RuffTool().select_rules(new_rules)

                # Assert
                rules = RuffTool().selected_rules()
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
            with change_cwd(tmp_path), PyprojectTOMLManager():
                RuffTool().select_rules(["C", "D"])

                # Assert
                rules = RuffTool().selected_rules()
            assert rules == ["A", "B", "C", "D"]

        def test_respects_order(self, tmp_path: Path):
            # Arrange
            (tmp_path / "pyproject.toml").write_text(
                """
[tool.ruff.lint]
select = ["D", "B", "A"]
"""
            )

            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                RuffTool().select_rules(["E", "C", "A"])

                # Assert
                assert RuffTool().selected_rules() == ["D", "B", "A", "C", "E"]

        def test_ruff_toml(self, tmp_path: Path):
            # Arrange
            (tmp_path / "ruff.toml").write_text(
                """
[lint]
select = ["A", "B"]
"""
            )

            # Act
            with change_cwd(tmp_path), RuffTOMLManager():
                RuffTool().select_rules(["C", "D"])

                # Assert
                rules = RuffTool().selected_rules()

            assert rules == ["A", "B", "C", "D"]

        def test_no_rules(self, tmp_path: Path):
            # Arrange
            (tmp_path / "pyproject.toml").write_text(
                """
[tool.ruff.lint]
select = ["A"]
"""
            )

            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                RuffTool().select_rules([])

                # Assert
                assert RuffTool().selected_rules() == ["A"]

        def test_specific_absorbed_by_existing_group(self, tmp_path: Path):
            # Adding "TC001" when "TC" exists should be a no-op
            # Arrange
            (tmp_path / "pyproject.toml").write_text(
                """\
[tool.ruff.lint]
select = ["TC"]
"""
            )

            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                result = RuffTool().select_rules(["TC001"])

                # Assert
                assert RuffTool().selected_rules() == ["TC"]
            assert not result

        def test_specific_absorbed_by_all(self, tmp_path: Path):
            # Adding any rule when "ALL" exists should be a no-op
            # Arrange
            (tmp_path / "pyproject.toml").write_text(
                """\
[tool.ruff.lint]
select = ["ALL"]
"""
            )

            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                result = RuffTool().select_rules(["TC001"])

                # Assert
                assert RuffTool().selected_rules() == ["ALL"]
            assert not result

        def test_group_replaces_specific(self, tmp_path: Path):
            # Adding "TC" when "TC001" exists should replace "TC001" with "TC"
            # Arrange
            (tmp_path / "pyproject.toml").write_text(
                """\
[tool.ruff.lint]
select = ["TC001"]
"""
            )

            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                result = RuffTool().select_rules(["TC"])

                # Assert
                assert RuffTool().selected_rules() == ["TC"]
            assert result

        def test_all_replaces_everything(self, tmp_path: Path):
            # Adding "ALL" should replace all existing rules
            # Arrange
            (tmp_path / "pyproject.toml").write_text(
                """\
[tool.ruff.lint]
select = ["A", "TC001", "E501"]
"""
            )

            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                result = RuffTool().select_rules(["ALL"])

                # Assert
                assert RuffTool().selected_rules() == ["ALL"]
            assert result

    class TestDeselectRules:
        def test_no_pyproject_toml(self, tmp_path: Path):
            # Act
            with change_cwd(tmp_path), files_manager():
                RuffTool().deselect_rules(["A"])

                # Assert
                assert RuffTool().selected_rules() == []

        def test_blank_slate(self, tmp_path: Path):
            # Arrange
            (tmp_path / "pyproject.toml").write_text("")

            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                RuffTool().deselect_rules(["A", "B", "C"])

                # Assert
                assert RuffTool().selected_rules() == []

        def test_single_rule(self, tmp_path: Path):
            # Arrange
            (tmp_path / "pyproject.toml").write_text(
                """
[tool.ruff.lint]
select = ["A"]
"""
            )

            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                RuffTool().deselect_rules(["A"])

                # Assert
                assert RuffTool().selected_rules() == []

        def test_mix(self, tmp_path: Path):
            # Arrange
            (tmp_path / "pyproject.toml").write_text(
                """
[tool.ruff.lint]
select = ["A", "B", "C"]
"""
            )

            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                RuffTool().deselect_rules(["A", "C"])

                # Assert
                assert RuffTool().selected_rules() == ["B"]

        def test_ruff_toml(self, tmp_path: Path):
            # Arrange
            (tmp_path / ".ruff.toml").write_text(
                """\
[lint]
select = ["A", "B"]
"""
            )

            # Act
            with change_cwd(tmp_path), DotRuffTOMLManager():
                RuffTool().deselect_rules(["A"])

                # Assert
                assert RuffTool().selected_rules() == ["B"]

    class TestIgnoreRules:
        def test_add_to_existing(self, tmp_path: Path):
            # Arrange
            (tmp_path / "pyproject.toml").write_text(
                """\
[tool.ruff.lint]
ignore = ["A", "B"]
"""
            )

            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                RuffTool().ignore_rules(["C", "D"])

                # Assert
                assert RuffTool().ignored_rules() == ["A", "B", "C", "D"]

        def test_no_rules(self, tmp_path: Path):
            # Arrange
            (tmp_path / "pyproject.toml").write_text(
                """\
[tool.ruff.lint]
ignore = ["A"]
"""
            )

            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                RuffTool().ignore_rules([])

                # Assert
                assert RuffTool().ignored_rules() == ["A"]

        def test_specific_absorbed_by_existing_group(self, tmp_path: Path):
            # Adding "TC001" when "TC" is already ignored should be a no-op
            # Arrange
            (tmp_path / "pyproject.toml").write_text(
                """\
[tool.ruff.lint]
ignore = ["TC"]
"""
            )

            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                result = RuffTool().ignore_rules(["TC001"])

                # Assert
                assert RuffTool().ignored_rules() == ["TC"]
            assert not result

        def test_group_replaces_specific(self, tmp_path: Path):
            # Adding "TC" when "TC001" is ignored should replace "TC001" with "TC"
            # Arrange
            (tmp_path / "pyproject.toml").write_text(
                """\
[tool.ruff.lint]
ignore = ["TC001"]
"""
            )

            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                result = RuffTool().ignore_rules(["TC"])

                # Assert
                assert RuffTool().ignored_rules() == ["TC"]
            assert result

        def test_preserves_comments(self, tmp_path: Path):
            # https://github.com/usethis-python/usethis-python/issues/884
            # Arrange
            (tmp_path / "ruff.toml").write_text(
                """\
lint.ignore = [
  "ANN401",  # This is too strict for dunder methods.
  "B023",    # Prevents using df.loc[lambda _: ...]; too many false positives.
  "B024",    # This is controversial, ABC's don't always need methods.
  "C408",    # This is controversial, calls to `dict` can be more idiomatic than {}.
]
"""
            )

            # Act
            with change_cwd(tmp_path), RuffTOMLManager():
                RuffTool().ignore_rules(["ERA001"])

            # Assert
            contents = (tmp_path / "ruff.toml").read_text()
            assert "# This is too strict for dunder methods." in contents
            assert "# Prevents using df.loc[lambda _: ..." in contents
            assert "# This is controversial, ABC's don't always need methods." in contents
            assert (
                "# This is controversial, calls to `dict` can be more idiomatic than {}."
                in contents
            )
            assert '"ERA001"' in contents

    class TestIsLinterUsed:
        def test_neither_subtool_has_config_assume_both_used(self, tmp_path: Path):
            # Act
            with change_cwd(tmp_path), files_manager():
                assert RuffTool().is_linter_used()

        def test_formatter_used(self, tmp_path: Path):
            # Arrange
            (tmp_path / "pyproject.toml").write_text(
                """\
[tool.ruff.format]
select = ["A"]
"""
            )
            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                assert not RuffTool().is_linter_used()

        def test_pyproject_toml(self, tmp_path: Path):
            # Arrange
            (tmp_path / "pyproject.toml").write_text(
                """\
[tool.ruff.lint]
select = ["A"]
"""
            )

            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                assert RuffTool().is_linter_used()

        def test_ruff_toml(self, tmp_path: Path):
            # Arrange
            (tmp_path / ".ruff.toml").write_text(
                """\
[lint]
select = ["A"]
"""
            )

            # Act
            with change_cwd(tmp_path), DotRuffTOMLManager():
                assert RuffTool().is_linter_used()

    class TestIsFormatterUsed:
        def test_neither_subtool_has_config_assume_both_used(self, tmp_path: Path):
            # Act
            with change_cwd(tmp_path), files_manager():
                assert RuffTool().is_formatter_used()

        def test_linter_used(self, tmp_path: Path):
            # Arrange
            (tmp_path / "pyproject.toml").write_text(
                """\
[tool.ruff.lint]
select = ["A"]
"""
            )

            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                assert not RuffTool().is_formatter_used()

        def test_pyproject_toml(self, tmp_path: Path):
            # Arrange
            (tmp_path / "pyproject.toml").write_text(
                """\
[tool.ruff.format]
select = ["A"]
"""
            )

            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                assert RuffTool().is_formatter_used()

        def test_ruff_toml(self, tmp_path: Path):
            # Arrange
            (tmp_path / ".ruff.toml").write_text(
                """\
[format]
select = ["A"]
"""
            )

            # Act
            with change_cwd(tmp_path), DotRuffTOMLManager():
                assert RuffTool().is_formatter_used()

    class TestIgnoreRulesInGlob:
        def test_dont_break_config(self, tmp_path: Path):
            # https://github.com/usethis-python/usethis-python/issues/862
            # The issue is basically the same as this one though:
            # https://github.com/usethis-python/usethis-python/issues/507
            # Arrange
            (tmp_path / "pyproject.toml").write_text("""\
[tool.ruff]
lint.select = [ "INP" ]
""")

            with change_cwd(tmp_path), files_manager():
                # Act
                RuffTool().ignore_rules_in_glob(["INP"], glob="tests/**")

            # Assert
            contents = (tmp_path / "pyproject.toml").read_text()
            assert (
                contents
                == """\
[tool.ruff]
lint.select = [ "INP" ]
lint.per-file-ignores."tests/**" = ["INP"]
"""
            )

        def test_specific_absorbed_by_existing_group(self, tmp_path: Path):
            # Adding "TC001" per-file-ignore when "TC" is already ignored should be a no-op
            # Arrange
            (tmp_path / "pyproject.toml").write_text("""\
[tool.ruff.lint.per-file-ignores]
"tests/**" = ["TC"]
""")

            with change_cwd(tmp_path), PyprojectTOMLManager():
                # Act
                RuffTool().ignore_rules_in_glob(["TC001"], glob="tests/**")

                # Assert
                assert RuffTool().get_ignored_rules_in_glob("tests/**") == ["TC"]

        def test_group_replaces_specific(self, tmp_path: Path):
            # Adding "TC" per-file-ignore when "TC001" exists should replace it
            # Arrange
            (tmp_path / "pyproject.toml").write_text("""\
[tool.ruff.lint.per-file-ignores]
"tests/**" = ["TC001"]
""")

            with change_cwd(tmp_path), PyprojectTOMLManager():
                # Act
                RuffTool().ignore_rules_in_glob(["TC"], glob="tests/**")

                # Assert
                assert RuffTool().get_ignored_rules_in_glob("tests/**") == ["TC"]

    class TestUnignoreRulesInGlob:
        def test_removes_rule(self, tmp_path: Path):
            # Arrange
            (tmp_path / "pyproject.toml").write_text("""\
[tool.ruff]
lint.select = [ "RUF" ]
lint.per-file-ignores."tests/**" = ["RUF059"]
""")

            with change_cwd(tmp_path), files_manager():
                # Act
                RuffTool().unignore_rules_in_glob(["RUF059"], glob="tests/**")

            # Assert
            contents = (tmp_path / "pyproject.toml").read_text()
            assert "RUF059" not in contents

        def test_no_op_when_not_ignored(
            self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
        ):
            # Arrange
            (tmp_path / "pyproject.toml").write_text("""\
[tool.ruff]
lint.select = [ "RUF" ]
""")

            with change_cwd(tmp_path), files_manager():
                # Act
                RuffTool().unignore_rules_in_glob(["RUF059"], glob="tests/**")

            # Assert - no changes, no output
            out, _err = capfd.readouterr()
            assert "RUF059" not in out

    class TestAddConfig:
        def test_empty_dir(self, tmp_path: Path):
            # Expect ruff.toml to be preferred

            # Act
            with change_cwd(tmp_path), files_manager():
                RuffTool(
                    # Needed to ensure the config is non-null (and so `ruff.toml` is
                    # written)
                    linter_detection="always",
                ).add_configs()

            # Assert
            assert not (tmp_path / ".ruff.toml").exists()
            assert not (tmp_path / "pyproject.toml").exists()
            assert (tmp_path / "ruff.toml").exists()

        def test_pyproject_toml_exists(self, tmp_path: Path):
            # Arrange
            (tmp_path / "pyproject.toml").touch()

            # Act
            with change_cwd(tmp_path), files_manager():
                RuffTool().add_configs()

            # Assert
            assert not (tmp_path / ".ruff.toml").exists()
            assert (tmp_path / "pyproject.toml").exists()
            assert not (tmp_path / "ruff.toml").exists()
