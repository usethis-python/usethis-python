from pathlib import Path

import pytest

from usethis._config_file import files_manager
from usethis._test import change_cwd
from usethis._tool.impl.requirements_txt import RequirementsTxtTool


class TestRequirementsTxtTool:
    class TestPrintHowToUse:
        def test_pre_commit_and_not_uv(
            self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
        ):
            # Arrange
            (tmp_path / ".pre-commit-config.yaml").write_text("""\
repos:
  - repo: local
    hooks:
      - id: uv-export
        name: uv-export
        entry: uv export --frozen --offline --quiet -o=requirements.txt
        language: system
        pass_filenames: false
        require_serial: true
""")

            # Act
            with change_cwd(tmp_path), files_manager():
                RequirementsTxtTool().print_how_to_use()

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert out == (
                "☐ Run 'pre-commit run uv-export' to write 'requirements.txt'.\n"
            )
