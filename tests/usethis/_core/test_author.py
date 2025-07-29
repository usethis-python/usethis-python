from pathlib import Path

import pytest

from usethis._core.author import add_author
from usethis._integrations.file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._integrations.file.toml.errors import (
    TOMLValueInvalidError,
    TOMLValueMissingError,
)
from usethis._test import change_cwd


class TestAddAuthor:
    def test_no_authors_yet(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
        # Arrange
        (tmp_path / "pyproject.toml").touch()

        # Act
        with change_cwd(tmp_path), PyprojectTOMLManager():
            add_author(
                name="John Cleese",
                email="jc@example.com",
            )

        # Assert
        assert (tmp_path / "pyproject.toml").read_text() == (
            """\

[[project.authors]]
name = "John Cleese"
email = "jc@example.com"
"""
        )
        out, err = capfd.readouterr()
        assert out == "✔ Setting 'John Cleese' as an author.\n"
        assert not err

    def test_append(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[project]
authors = [
    { name="First Contributor" }
]
"""
        )

        # Act
        with change_cwd(tmp_path), PyprojectTOMLManager():
            add_author(
                name="John Cleese",
                email="jc@example.com",
            )

        # Assert
        assert (tmp_path / "pyproject.toml").read_text() == (
            """\


[[project.authors]]
name = "First Contributor"
[[project.authors]]
name = "John Cleese"
email = "jc@example.com"
"""
        )

    def test_email_not_provided(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").touch()

        # Act
        with change_cwd(tmp_path), PyprojectTOMLManager():
            add_author(name="John Cleese")

        # Assert
        assert (tmp_path / "pyproject.toml").read_text() == (
            """\

[[project.authors]]
name = "John Cleese"
"""
        )

    def test_overwrite(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[project]

[[project.authors]]
name = "First Contributor"
[[project.authors]]
name = "John Cleese"
email = "jc@example.com"
"""
        )

        # Act
        with change_cwd(tmp_path), PyprojectTOMLManager():
            add_author(
                name="Python Dev Team",
                overwrite=True,
            )

        # Assert
        assert (tmp_path / "pyproject.toml").read_text() == (
            """\
[project]

[[project.authors]]
name = "Python Dev Team"
"""
        )

    def test_no_pyproject_yet(self, tmp_path: Path):
        # Act
        with change_cwd(tmp_path), PyprojectTOMLManager():
            add_author(name="John Cleese")

        # Assert
        assert "John Cleese" in (tmp_path / "pyproject.toml").read_text()

    def test_doesnt_break_other_sections(self, tmp_path: Path):
        # There is a bug in tomlkit I suspect, we needed a bit of a bespoke workaround.
        # Suspected to be similar to this https://github.com/python-poetry/tomlkit/issues/381

        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[project]
authors = [
  { name = "Python Dev"},
]
scripts.usethis = "usethis.__main__:app"
"""
        )

        # Act
        with change_cwd(tmp_path), PyprojectTOMLManager() as manager:
            add_author(name="John Cleese")
            assert ["project", "scripts"] in manager

        # Assert
        with change_cwd(tmp_path), PyprojectTOMLManager() as manager:
            assert ["project"] in manager
            assert ["project", "scripts"] in manager

    def test_project_section_not_a_mapping(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
project = ["a"]
"""
        )

        # Act
        with (
            change_cwd(tmp_path),
            PyprojectTOMLManager(),
            pytest.raises(
                TOMLValueMissingError,
                match="'project' is not a valid mapping .* does not contain the key 'authors'",
            ),
        ):
            add_author(name="John Cleese")

    def test_authors_section_not_a_list(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[project]
authors = { name = "Python Dev" }
"""
        )

        # Act
        with (
            change_cwd(tmp_path),
            PyprojectTOMLManager(),
            pytest.raises(
                TOMLValueInvalidError, match="'project.authors' is not a valid list"
            ),
        ):
            add_author(name="John Cleese")
