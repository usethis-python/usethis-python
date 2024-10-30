import subprocess
from pathlib import Path

import pytest

from usethis._integrations.pre_commit.core import _VALIDATEPYPROJECT_VERSION
from usethis._integrations.pre_commit.hooks import (
    _HOOK_ORDER,
    get_hook_names,
)
from usethis._integrations.uv.deps import (
    add_deps_to_group,
    get_deps_from_group,
)
from usethis._interface.tool import _deptry, _pre_commit, _pytest, _ruff
from usethis._tool import ALL_TOOLS
from usethis._utils._test import change_cwd, is_offline


class TestAllHooksList:
    def test_subset_hook_names(self):
        for tool in ALL_TOOLS:
            try:
                hook_names = [
                    hook.id for hook in tool.get_pre_commit_repo_config().hooks
                ]
            except NotImplementedError:
                continue
            for hook_name in hook_names:
                assert hook_name in _HOOK_ORDER


class TestPreCommit:
    class TestAdd:
        def test_dependency_added(self, uv_init_dir: Path):
            # Act
            with change_cwd(uv_init_dir):
                _pre_commit(offline=is_offline())

                # Assert
                (dev_dep,) = get_deps_from_group("dev")
            assert dev_dep == "pre-commit"

        def test_stdout(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
            # Act
            with change_cwd(uv_init_dir):
                _pre_commit(offline=is_offline())

            # Assert
            out, _ = capfd.readouterr()
            assert out == (
                "✔ Adding 'pre-commit' to the 'dev' dependency group.\n"
                "✔ Writing '.pre-commit-config.yaml'.\n"
                "✔ Ensuring pre-commit hooks are installed.\n"
                "☐ Call the 'pre-commit run --all-files' command to run the hooks manually.\n"
            )

        def test_config_file_exists(self, uv_init_dir: Path):
            # Act
            with change_cwd(uv_init_dir):
                _pre_commit(offline=is_offline())

            # Assert
            assert (uv_init_dir / ".pre-commit-config.yaml").exists()

        def test_config_file_contents(self, uv_init_dir: Path):
            # Act
            with change_cwd(uv_init_dir):
                _pre_commit(offline=is_offline())

            # Assert
            contents = (uv_init_dir / ".pre-commit-config.yaml").read_text()
            assert contents == (
                f"""\
repos:
  - repo: https://github.com/abravalheri/validate-pyproject
    rev: "{_VALIDATEPYPROJECT_VERSION}"
    hooks:
      - id: validate-pyproject
        additional_dependencies: ["validate-pyproject-schema-store[all]"]
"""
            )

        def test_already_exists(self, uv_init_repo_dir: Path):
            # Arrange
            (uv_init_repo_dir / ".pre-commit-config.yaml").write_text(
                """\
repos:
- repo: foo
    hooks:
    - id: bar
"""
            )

            # Act
            with change_cwd(uv_init_repo_dir):
                _pre_commit(offline=is_offline())

            # Assert
            contents = (uv_init_repo_dir / ".pre-commit-config.yaml").read_text()
            assert contents == (
                """\
repos:
- repo: foo
    hooks:
    - id: bar
"""
            )

        def test_bad_commit(self, uv_init_repo_dir: Path):
            # Act
            with change_cwd(uv_init_repo_dir):
                _pre_commit(offline=is_offline())
            subprocess.run(["git", "add", "."], cwd=uv_init_repo_dir, check=True)
            subprocess.run(
                ["git", "commit", "-m", "Good commit"], cwd=uv_init_repo_dir, check=True
            )

            # Assert
            (uv_init_repo_dir / "pyproject.toml").write_text("[")
            subprocess.run(["git", "add", "."], cwd=uv_init_repo_dir, check=True)
            with pytest.raises(subprocess.CalledProcessError):
                subprocess.run(
                    ["git", "commit", "-m", "Bad commit"],
                    cwd=uv_init_repo_dir,
                    check=True,
                )

        def test_cli_pass(self, uv_init_repo_dir: Path):
            if not is_offline():
                subprocess.run(
                    ["usethis", "tool", "pre-commit"], cwd=uv_init_repo_dir, check=True
                )
            else:
                subprocess.run(
                    ["usethis", "tool", "pre-commit", "--offline"],
                    cwd=uv_init_repo_dir,
                    check=True,
                )

            subprocess.run(
                ["uv", "run", "pre-commit", "run", "--all-files"],
                cwd=uv_init_repo_dir,
                check=True,
            )

        def test_cli_fail(self, uv_init_repo_dir: Path):
            if not is_offline():
                subprocess.run(
                    ["usethis", "tool", "pre-commit"], cwd=uv_init_repo_dir, check=True
                )
            else:
                subprocess.run(
                    ["usethis", "tool", "pre-commit", "--offline"],
                    cwd=uv_init_repo_dir,
                    check=True,
                )

            # Pass invalid TOML to fail the pre-commit for validate-pyproject
            (uv_init_repo_dir / "pyproject.toml").write_text("[")
            try:
                subprocess.run(
                    ["uv", "run", "pre-commit", "run", "--all-files"],
                    cwd=uv_init_repo_dir,
                    check=True,
                )
            except subprocess.CalledProcessError:
                pass
            else:
                pytest.fail("Expected subprocess.CalledProcessError")

    class TestRemove:
        def test_config_file(self, uv_init_dir: Path):
            # Arrange
            (uv_init_dir / ".pre-commit-config.yaml").touch()

            # Act
            with change_cwd(uv_init_dir):
                _pre_commit(remove=True, offline=is_offline())

            # Assert
            assert not (uv_init_dir / ".pre-commit-config.yaml").exists()

        def test_dep(self, uv_init_dir: Path):
            with change_cwd(uv_init_dir):
                # Arrange
                add_deps_to_group(["pre-commit"], "dev", offline=is_offline())

                # Act
                _pre_commit(remove=True, offline=is_offline())

                # Assert
                assert not get_deps_from_group("dev")


class TestDeptry:
    def test_dependency_added(self, uv_init_dir: Path):
        # Act
        with change_cwd(uv_init_dir):
            _deptry()

            # Assert
            (dev_dep,) = get_deps_from_group("dev")
        assert dev_dep == "deptry"

    def test_stdout(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
        # Act
        with change_cwd(uv_init_dir):
            _deptry()

        # Assert
        out, _ = capfd.readouterr()
        assert out == (
            "✔ Adding 'deptry' to the 'dev' dependency group.\n"
            "☐ Call the 'deptry src' command to run deptry.\n"
        )

    def test_run_deptry_fail(self, uv_init_dir: Path):
        # Arrange
        f = uv_init_dir / "bad.py"
        f.write_text("import broken_dependency")

        # Act
        with change_cwd(uv_init_dir):
            _deptry()

        # Assert
        with pytest.raises(subprocess.CalledProcessError):
            subprocess.run(["deptry", "."], cwd=uv_init_dir, check=True)

    def test_run_deptry_pass(self, uv_init_dir: Path):
        # Arrange
        f = uv_init_dir / "good.py"
        f.write_text("import sys")

        # Act
        with change_cwd(uv_init_dir):
            _deptry()

        # Assert
        subprocess.run(["deptry", "."], cwd=uv_init_dir, check=True)

    def test_cli(self, uv_init_dir: Path):
        subprocess.run(["usethis", "tool", "deptry"], cwd=uv_init_dir, check=True)

    def test_pre_commit_after(
        self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]
    ):
        # Act
        with change_cwd(uv_init_dir):
            _deptry(offline=is_offline())
            _pre_commit(offline=is_offline())

            # Assert
            hook_names = get_hook_names()

        # 1. File exists
        assert (uv_init_dir / ".pre-commit-config.yaml").exists()

        # 2. Hook is in the file
        assert "deptry" in hook_names

        # 3. Test file contents
        assert (uv_init_dir / ".pre-commit-config.yaml").read_text() == (
            f"""\
repos:
  - repo: https://github.com/abravalheri/validate-pyproject
    rev: {_VALIDATEPYPROJECT_VERSION}
    hooks:
      - id: validate-pyproject
        additional_dependencies: ['validate-pyproject-schema-store[all]']
  - repo: local
    hooks:
      - id: deptry
        name: deptry
        entry: uv run --frozen deptry src
        language: system
        always_run: true
        pass_filenames: false
"""
        )

        # 4. Check messages
        out, _ = capfd.readouterr()
        assert out == (
            "✔ Adding 'deptry' to the 'dev' dependency group.\n"
            "☐ Call the 'deptry src' command to run deptry.\n"
            "✔ Adding 'pre-commit' to the 'dev' dependency group.\n"
            "✔ Writing '.pre-commit-config.yaml'.\n"
            "✔ Adding deptry config to '.pre-commit-config.yaml'.\n"
            "✔ Ensuring pre-commit hooks are installed.\n"
            "☐ Call the 'pre-commit run --all-files' command to run the hooks manually.\n"
        )

    def test_pre_commit_first(
        self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]
    ):
        # Act
        with change_cwd(uv_init_dir):
            _pre_commit(offline=is_offline())
            _deptry(offline=is_offline())

            # Assert
            hook_names = get_hook_names()

        # 1. File exists
        assert (uv_init_dir / ".pre-commit-config.yaml").exists()

        # 2. Hook is in the file
        assert "deptry" in hook_names

        # 3. Test file contents
        assert (uv_init_dir / ".pre-commit-config.yaml").read_text() == (
            f"""repos:
  - repo: https://github.com/abravalheri/validate-pyproject
    rev: {_VALIDATEPYPROJECT_VERSION}
    hooks:
      - id: validate-pyproject
        additional_dependencies: ['validate-pyproject-schema-store[all]']
  - repo: local
    hooks:
      - id: deptry
        name: deptry
        entry: uv run --frozen deptry src
        language: system
        always_run: true
        pass_filenames: false
"""
        )

        # 4. Check messages
        out, _ = capfd.readouterr()
        assert out == (
            "✔ Adding 'pre-commit' to the 'dev' dependency group.\n"
            "✔ Writing '.pre-commit-config.yaml'.\n"
            "✔ Ensuring pre-commit hooks are installed.\n"
            "☐ Call the 'pre-commit run --all-files' command to run the hooks manually.\n"
            "✔ Adding 'deptry' to the 'dev' dependency group.\n"
            "✔ Adding deptry config to '.pre-commit-config.yaml'.\n"
            "☐ Call the 'deptry src' command to run deptry.\n"
        )


class TestRuff:
    class TestAdd:
        def test_dependency_added(self, uv_init_dir: Path):
            # Act
            with change_cwd(uv_init_dir):
                _ruff(offline=is_offline())

                # Assert
                (dev_dep,) = get_deps_from_group("dev")
            assert dev_dep == "ruff"

        def test_stdout(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
            # Act
            with change_cwd(uv_init_dir):
                _ruff(offline=is_offline())

            # Assert
            out, _ = capfd.readouterr()
            assert out == (
                "✔ Adding 'ruff' to the 'dev' dependency group.\n"
                "✔ Adding ruff config to 'pyproject.toml'.\n"
                "✔ Enabling ruff rules 'C4', 'E4', 'E7', 'E9', 'F', 'FURB', 'I', 'PLE', 'PLR', \n'RUF', 'SIM', 'UP' in 'pyproject.toml'.\n"
                "☐ Call the 'ruff check --fix' command to run the ruff linter with autofixes.\n"
                "☐ Call the 'ruff format' command to run the ruff formatter.\n"
            )

        def test_cli(self, uv_init_dir: Path):
            if not is_offline():
                subprocess.run(["usethis", "tool", "ruff"], cwd=uv_init_dir, check=True)
            else:
                subprocess.run(
                    ["usethis", "tool", "ruff", "--offline"],
                    cwd=uv_init_dir,
                    check=True,
                )

        def test_pre_commit_first(
            self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]
        ):
            # Act
            with change_cwd(uv_init_dir):
                _ruff(offline=is_offline())
                _pre_commit(offline=is_offline())

                # Assert
                hook_names = get_hook_names()

            assert "ruff-format" in hook_names
            assert "ruff-check" in hook_names

    class TestRemove:
        def test_config_file(self, uv_init_dir: Path):
            # Arrange
            (uv_init_dir / "pyproject.toml").write_text(
                """\
[tool.ruff.lint]
select = ["A", "B", "C"]
"""
            )

            # Act
            with change_cwd(uv_init_dir):
                _ruff(remove=True, offline=is_offline())

            # Assert
            assert (uv_init_dir / "pyproject.toml").read_text() == ""

        def test_blank_slate(self, uv_init_dir: Path):
            # Arrange
            contents = (uv_init_dir / "pyproject.toml").read_text()

            # Act
            with change_cwd(uv_init_dir):
                _ruff(remove=True, offline=is_offline())

            # Assert
            assert (uv_init_dir / "pyproject.toml").read_text() == contents

        def test_roundtrip(self, uv_init_dir: Path):
            # Arrange
            contents = (uv_init_dir / "pyproject.toml").read_text()

            # Act
            with change_cwd(uv_init_dir):
                _ruff(offline=is_offline())
                _ruff(remove=True, offline=is_offline())

            # Assert
            assert (
                (uv_init_dir / "pyproject.toml").read_text()
                == contents
                + """\

[dependency-groups]
dev = []

"""
            )


class TestPytest:
    class TestAdd:
        def test_dep(self, uv_init_dir: Path):
            with change_cwd(uv_init_dir):
                _pytest(offline=is_offline())

                assert {
                    "pytest",
                    "pytest-md",
                    "pytest-cov",
                    "coverage",
                } <= set(get_deps_from_group("test"))

    class TestRemove:
        class TestRuffIntegration:
            def test_deselected(self, uv_init_dir: Path):
                # Arrange
                (uv_init_dir / "pyproject.toml").write_text(
                    """\
[tool.ruff.lint]
select = ["E", "PT"]
"""
                )

                # Act
                with change_cwd(uv_init_dir):
                    _pytest(remove=True, offline=is_offline())

                # Assert
                assert (uv_init_dir / "pyproject.toml").read_text() == (
                    """\
[tool.ruff.lint]
select = ["E"]
"""
                )

            def test_message(
                self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]
            ):
                # Arrange
                (uv_init_dir / "pyproject.toml").write_text(
                    """\
[tool.ruff.lint]
select = ["PT"]
"""
                )

                # Act
                with change_cwd(uv_init_dir):
                    _pytest(remove=True, offline=is_offline())

                # Assert
                out, _ = capfd.readouterr()
                assert out == ("✔ Disabling ruff rule 'PT' in 'pyproject.toml'.\n")

        class TestPyproject:
            def test_removed(self, uv_init_dir: Path):
                # Arrange
                (uv_init_dir / "pyproject.toml").write_text(
                    """\
    [tool.pytest]
    foo = "bar"
    """
                )

                # Act
                with change_cwd(uv_init_dir):
                    _pytest(remove=True, offline=is_offline())

                # Assert
                assert (uv_init_dir / "pyproject.toml").read_text() == ""

            def test_message(
                self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]
            ):
                # Arrange
                (uv_init_dir / "pyproject.toml").write_text(
                    """\
    [tool.pytest]
    foo = "bar"
    """
                )

                # Act
                with change_cwd(uv_init_dir):
                    _pytest(remove=True, offline=is_offline())

                # Assert
                out, _ = capfd.readouterr()
                # N.B. we don't put `pytest` in quotes because we are referring to the
                # tool, not the package.
                assert out == "✔ Removing pytest config from 'pyproject.toml'.\n"

        class Dependencies:
            def test_removed(self, uv_init_dir: Path):
                # Arrange
                add_deps_to_group(["pytest"], "test", offline=is_offline())

                # Act
                with change_cwd(uv_init_dir):
                    _pytest(remove=True, offline=is_offline())

                # Assert
                assert not get_deps_from_group("test")
