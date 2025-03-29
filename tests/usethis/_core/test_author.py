from pathlib import Path

from usethis._core.author import add_author
from usethis._integrations.file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._test import change_cwd


class TestAddAuthor:
    def test_no_authors_yet(self, tmp_path: Path):
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
[project]

[[project.authors]]
name = "First Contributor"
[[project.authors]]
name = "John Cleese"
email = "jc@example.com"
"""
        )
        # TODO is this format change acceptable?

    # TODO test append behaviour
    # TODO overwrite option
