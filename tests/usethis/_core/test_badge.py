from pathlib import Path

import pytest

from usethis._core.badge import add_badge
from usethis._test import change_cwd


class TestAddBadge:
    def test_empty(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
        # Arrange
        path = tmp_path / "README.md"
        path.write_text("""\
""")

        # Act
        with change_cwd(tmp_path):
            add_badge(
                markdown="![Licence](<https://img.shields.io/badge/licence-mit-green>)",
                badge_name="license",
            )

        # Assert
        assert (
            path.read_text()
            == """\
![Licence](<https://img.shields.io/badge/licence-mit-green>)
"""
        )
        out, err = capfd.readouterr()
        assert not err
        assert out == "✔ Adding license badge to 'README.md'.\n"

    def test_only_newline(self, tmp_path: Path):
        # Arrange
        path = tmp_path / "README.md"
        path.write_text("""\

""")

        # Act
        with change_cwd(tmp_path):
            add_badge(
                markdown="![Licence](<https://img.shields.io/badge/licence-mit-green>)",
                badge_name="license",
            )

        # Assert
        assert (
            path.read_text()
            == """\
![Licence](<https://img.shields.io/badge/licence-mit-green>)
"""
        )

    def test_predecessor(self, tmp_path: Path):
        # Arrange
        path = tmp_path / "README.md"
        path.write_text("""\
[![Ruff](<https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json>)](<https://github.com/astral-sh/ruff>)
""")

        # Act
        with change_cwd(tmp_path):
            add_badge(
                markdown="[![pre-commit](<https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit>)](<https://github.com/pre-commit/pre-commit>)",
                badge_name="pre-commit",
            )

        # Assert
        content = path.read_text()
        assert (
            content
            == """\
[![Ruff](<https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json>)](<https://github.com/astral-sh/ruff>)
[![pre-commit](<https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit>)](<https://github.com/pre-commit/pre-commit>)
"""
        )

    def test_not_predecessor(self, tmp_path: Path):
        # Arrange
        path = tmp_path / "README.md"
        path.write_text("""\
[![pre-commit](<https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit>)](<https://github.com/pre-commit/pre-commit>)
""")

        # Act
        with change_cwd(tmp_path):
            add_badge(
                markdown="[![Ruff](<https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json>)](<https://github.com/astral-sh/ruff>)",
                badge_name="ruff",
            )

        # Assert
        content = path.read_text()
        assert (
            content
            == """\
[![Ruff](<https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json>)](<https://github.com/astral-sh/ruff>)
[![pre-commit](<https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit>)](<https://github.com/pre-commit/pre-commit>)
"""
        )

    def test_not_recognized_gets_put_after_known_order(self, tmp_path: Path):
        # Arrange
        path = tmp_path / "README.md"
        path.write_text("""\
[![Ruff](<https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json>)](<https://github.com/astral-sh/ruff>)
""")

        # Act
        with change_cwd(tmp_path):
            add_badge(
                markdown="![Don't Know What This Is](<https://example.com>)",
                badge_name="unknown",
            )

        # Assert
        content = path.read_text()
        assert (
            content
            == """\
[![Ruff](<https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json>)](<https://github.com/astral-sh/ruff>)
![Don't Know What This Is](<https://example.com>)
"""
        )

    def test_skip_header1(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
        # Arrange
        path = tmp_path / "README.md"
        path.write_text("""\
# Header
""")

        # Act
        with change_cwd(tmp_path):
            add_badge(
                markdown="![Licence](<https://img.shields.io/badge/licence-mit-green>)",
                badge_name="license",
            )

        # Assert
        assert (
            path.read_text()
            == """\
# Header

![Licence](<https://img.shields.io/badge/licence-mit-green>)
"""
        )
        out, err = capfd.readouterr()
        assert not err
        assert out == "✔ Adding license badge to 'README.md'.\n"

    def test_skip_header2(self, tmp_path: Path):
        # Arrange
        path = tmp_path / "README.md"
        path.write_text("""\
## Header
""")

        # Act
        with change_cwd(tmp_path):
            add_badge(
                markdown="![Licence](<https://img.shields.io/badge/licence-mit-green>)",
                badge_name="license",
            )

        # Assert
        assert (
            path.read_text()
            == """\
## Header

![Licence](<https://img.shields.io/badge/licence-mit-green>)
"""
        )

    def test_skip_header_with_extra_newline(self, tmp_path: Path):
        # Arrange
        path = tmp_path / "README.md"
        path.write_text("""\
# Header

""")

        # Act
        with change_cwd(tmp_path):
            add_badge(
                markdown="![Licence](<https://img.shields.io/badge/licence-mit-green>)",
                badge_name="license",
            )

        # Assert
        assert (
            path.read_text()
            == """\
# Header

![Licence](<https://img.shields.io/badge/licence-mit-green>)
"""
        )

    def test_extra_unstripped_space(self, tmp_path: Path):
        # Arrange
        path = tmp_path / "README.md"
        path.write_text("""\
  # Header  
  
 [![Ruff](<https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json>)](<https://github.com/astral-sh/ruff>)
""")

        # Act
        with change_cwd(tmp_path):
            add_badge(
                markdown="[![pre-commit](<https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit>)](<https://github.com/pre-commit/pre-commit>)",
                badge_name="pre-commit",
            )

        # Assert
        content = path.read_text()
        assert (
            content
            == """\
  # Header  
  
 [![Ruff](<https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json>)](<https://github.com/astral-sh/ruff>)
[![pre-commit](<https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit>)](<https://github.com/pre-commit/pre-commit>)
"""
        )

    def test_already_exists(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
        # Arrange
        path = tmp_path / "README.md"
        path.write_text("""\
![Licence](<https://img.shields.io/badge/licence-mit-green>)
""")

        # Act
        with change_cwd(tmp_path):
            add_badge(
                markdown="![Licence](<https://img.shields.io/badge/licence-mit-green>)",
                badge_name="license",
            )

        # Assert
        assert (
            path.read_text()
            == """\
![Licence](<https://img.shields.io/badge/licence-mit-green>)
"""
        )
        out, err = capfd.readouterr()
        assert not err
        assert not out

    def test_badge_followed_by_text(self, tmp_path: Path):
        # Arrange
        path = tmp_path / "README.md"
        path.write_text("""\
# Header

Some text
""")

        # Act
        with change_cwd(tmp_path):
            add_badge(
                markdown="![Licence](<https://img.shields.io/badge/licence-mit-green>)",
                badge_name="license",
            )

        # Assert
        assert (
            path.read_text()
            == """\
# Header

![Licence](<https://img.shields.io/badge/licence-mit-green>)

Some text
"""
        )
