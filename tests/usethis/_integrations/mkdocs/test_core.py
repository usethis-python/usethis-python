from pathlib import Path

import pytest

from usethis._config_file import files_manager
from usethis._integrations.mkdocs.core import add_docs_dir
from usethis._test import change_cwd


class TestAddDocsDir:
    def test_from_empty(
        self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
    ) -> None:
        # Act
        with change_cwd(tmp_path), files_manager():
            add_docs_dir()

        # Assert
        assert (tmp_path / "docs").exists()
        assert (tmp_path / "docs" / "index.md").exists()
        out, err = capfd.readouterr()
        assert not err
        assert out == "✔ Creating '/docs'.\n"

    def test_docs_dir_exists(
        self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
    ) -> None:
        # Arrange
        (tmp_path / "docs").mkdir()

        # Act
        with change_cwd(tmp_path), files_manager():
            add_docs_dir()

        # Assert
        assert (tmp_path / "docs" / "index.md").exists()
        out, err = capfd.readouterr()
        assert not err
        assert out == "✔ Writing '/docs/index.md'.\n"

    def test_index_md_exists(
        self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
    ) -> None:
        # Arrange
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "index.md").write_text("Existing content")

        # Act
        with change_cwd(tmp_path), files_manager():
            add_docs_dir()

        # Assert
        out, err = capfd.readouterr()
        assert not err
        assert out == ""
