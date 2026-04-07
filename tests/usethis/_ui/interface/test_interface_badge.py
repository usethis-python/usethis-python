from pathlib import Path

from _test import CliRunner, change_cwd
from usethis._ui.interface.badge import app


class TestPyPI:
    def test_add(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["pypi"])

        # Assert
        assert result.exit_code == 0, result.output

    def test_remove(self, tmp_path: Path):
        # Arrange
        (tmp_path / "README.md").write_text("")

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["pypi", "--remove"])

        # Assert
        assert result.exit_code == 0, result.output

    def test_show(self, tmp_path: Path):
        # Arrange
        (tmp_path / "README.md").write_text("")

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["pypi", "--show"])

        # Assert
        assert result.exit_code == 0, result.output


class TestRuff:
    def test_add(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["ruff"])

        # Assert
        assert result.exit_code == 0, result.output

    def test_remove(self, tmp_path: Path):
        # Arrange
        (tmp_path / "README.md").write_text("")

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["ruff", "--remove"])

        # Assert
        assert result.exit_code == 0, result.output

    def test_wrong_encoding(self, tmp_path: Path):
        # Arrange
        (tmp_path / "README.md").write_text("utf-8", encoding="utf-16")

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["ruff"])

        # Assert
        assert result.exit_code == 0, result.output

    def test_show(self, tmp_path: Path):
        # Arrange
        (tmp_path / "README.md").write_text("")

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["ruff", "--show"])

        # Assert
        assert result.exit_code == 0, result.output


class TestTy:
    def test_add(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["ty"])

        # Assert
        assert result.exit_code == 0, result.output

    def test_remove(self, tmp_path: Path):
        # Arrange
        (tmp_path / "README.md").write_text("")

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["ty", "--remove"])

        # Assert
        assert result.exit_code == 0, result.output

    def test_show(self, tmp_path: Path):
        # Arrange
        (tmp_path / "README.md").write_text("")

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["ty", "--show"])

        # Assert
        assert result.exit_code == 0, result.output
        assert (
            result.output
            == "[![ty](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json)](https://github.com/astral-sh/ty)\n"
        )


class TestSocket:
    def test_add(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["socket"])

        # Assert
        assert result.exit_code == 0, result.output


class TestPreCommit:
    def test_add(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["pre-commit"])

        # Assert
        assert result.exit_code == 0, result.output

    def test_remove(self, tmp_path: Path):
        # Arrange
        (tmp_path / "README.md").write_text("")

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["pre-commit", "--remove"])

        # Assert
        assert result.exit_code == 0, result.output

    def test_show(self, tmp_path: Path):
        # Arrange
        (tmp_path / "README.md").write_text("")

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["pre-commit", "--show"])

        # Assert
        assert result.exit_code == 0, result.output


class TestUsethis:
    def test_add(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["usethis"])

        # Assert
        assert result.exit_code == 0, result.output

    def test_remove(self, tmp_path: Path):
        # Arrange
        (tmp_path / "README.md").write_text("")

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["usethis", "--remove"])

        # Assert
        assert result.exit_code == 0, result.output

    def test_show(self, tmp_path: Path):
        # Arrange
        (tmp_path / "README.md").write_text("")

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["usethis", "--show"])

        # Assert
        assert result.exit_code == 0, result.output
        assert (
            result.output
            == "[![usethis](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/usethis-python/usethis-python/main/assets/badge/v1.json)](https://github.com/usethis-python/usethis-python)\n"
        )


class TestBitbucket:
    def test_add(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["bitbucket"])

        # Assert
        assert result.exit_code == 0, result.output

    def test_remove(self, tmp_path: Path):
        # Arrange
        (tmp_path / "README.md").write_text("")

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["bitbucket", "--remove"])

        # Assert
        assert result.exit_code == 0, result.output

    def test_show(self, tmp_path: Path):
        # Arrange
        (tmp_path / "README.md").write_text("")

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["bitbucket", "--show"])

        # Assert
        assert result.exit_code == 0, result.output
        assert (
            result.output
            == "[![Bitbucket](https://img.shields.io/badge/Bitbucket-0747a6?logo=bitbucket&logoColor=white)](https://bitbucket.org)\n"
        )


class TestUV:
    def test_add(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["uv"])

        # Assert
        assert result.exit_code == 0, result.output

    def test_remove(self, tmp_path: Path):
        # Arrange
        (tmp_path / "README.md").write_text("")

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["uv", "--remove"])

        # Assert
        assert result.exit_code == 0, result.output

    def test_show(self, tmp_path: Path):
        # Arrange
        (tmp_path / "README.md").write_text("")

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke_safe(app, ["uv", "--show"])

        # Assert
        assert result.exit_code == 0, result.output
