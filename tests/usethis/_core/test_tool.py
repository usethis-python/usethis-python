import subprocess
from pathlib import Path

import pytest

from usethis._config import usethis_config
from usethis._core.ci import use_ci_bitbucket
from usethis._core.tool import (
    use_deptry,
    use_pre_commit,
    use_pyproject_fmt,
    use_pytest,
    use_ruff,
)
from usethis._integrations.pre_commit.hooks import (
    _HOOK_ORDER,
    get_hook_names,
)
from usethis._integrations.uv.deps import (
    add_deps_to_group,
    get_deps_from_group,
)
from usethis._test import change_cwd
from usethis._tool import ALL_TOOLS


class TestAllHooksList:
    def test_subset_hook_names(self):
        for tool in ALL_TOOLS:
            try:
                hook_names = [
                    hook.id
                    for repo_config in tool.get_pre_commit_repos()
                    for hook in repo_config.hooks or []
                ]
            except NotImplementedError:
                continue
            for hook_name in hook_names:
                assert hook_name in _HOOK_ORDER


class TestDeptry:
    class TestAdd:
        def test_dependency_added(self, uv_init_dir: Path, vary_network_conn: None):
            # Act
            with change_cwd(uv_init_dir):
                use_deptry()

                # Assert
                (dev_dep,) = get_deps_from_group("dev")
            assert dev_dep == "deptry"

        def test_stdout(
            self,
            uv_init_dir: Path,
            capfd: pytest.CaptureFixture[str],
            vary_network_conn: None,
        ):
            # Act
            with change_cwd(uv_init_dir):
                use_deptry()

            # Assert
            out, _ = capfd.readouterr()
            assert out == (
                "✔ Adding 'deptry' to the 'dev' dependency group.\n"
                "☐ Call the 'deptry src' command to run deptry.\n"
            )

        def test_run_deptry_fail(self, uv_init_dir: Path, vary_network_conn: None):
            # Arrange
            f = uv_init_dir / "bad.py"
            f.write_text("import broken_dependency")

            # Act
            with change_cwd(uv_init_dir):
                use_deptry()

            # Assert
            with pytest.raises(subprocess.CalledProcessError):
                subprocess.run(["deptry", "."], cwd=uv_init_dir, check=True)

        def test_run_deptry_pass(self, uv_init_dir: Path, vary_network_conn: None):
            # Arrange
            f = uv_init_dir / "good.py"
            f.write_text("import sys")

            # Act
            with change_cwd(uv_init_dir):
                use_deptry()

            # Assert
            subprocess.run(["deptry", "."], cwd=uv_init_dir, check=True)

        def test_pre_commit_after(
            self,
            uv_init_repo_dir: Path,
            capfd: pytest.CaptureFixture[str],
            vary_network_conn: None,
        ):
            # Act
            with change_cwd(uv_init_repo_dir):
                use_deptry()
                use_pre_commit()

                # Assert
                hook_names = get_hook_names()

            # 1. File exists
            assert (uv_init_repo_dir / ".pre-commit-config.yaml").exists()

            # 2. Hook is in the file
            assert "deptry" in hook_names

            # 3. Test file contents
            assert (uv_init_repo_dir / ".pre-commit-config.yaml").read_text() == (
                """\
repos:
  - repo: local
    hooks:
      - id: deptry
        name: deptry
        always_run: true
        entry: uv run --frozen deptry src
        language: system
"""
            )

            # 4. Check messages
            out, _ = capfd.readouterr()
            assert out == (
                "✔ Adding 'deptry' to the 'dev' dependency group.\n"
                "☐ Call the 'deptry src' command to run deptry.\n"
                "✔ Adding 'pre-commit' to the 'dev' dependency group.\n"
                "✔ Writing '.pre-commit-config.yaml'.\n"
                "✔ Adding hook 'deptry' to '.pre-commit-config.yaml'.\n"
                "✔ Ensuring pre-commit hooks are installed.\n"
                "☐ Call the 'pre-commit run --all-files' command to run the hooks manually.\n"
            )

    class TestRemove:
        def test_dep(self, uv_init_dir: Path, vary_network_conn: None):
            with change_cwd(uv_init_dir):
                # Arrange
                add_deps_to_group(["deptry"], "dev")

                # Act
                use_deptry(remove=True)

                # Assert
                assert not get_deps_from_group("dev")

    class TestPreCommitIntegration:
        def test_pre_commit_first(
            self,
            uv_init_repo_dir: Path,
            capfd: pytest.CaptureFixture[str],
            vary_network_conn: None,
        ):
            """Basically this checks that the placeholders gets removed."""

            with change_cwd(uv_init_repo_dir):
                # Arrange
                use_pre_commit()
                capfd.readouterr()

                # Act
                use_deptry()

                # Assert
                hook_names = get_hook_names()

            # 1. File exists
            assert (uv_init_repo_dir / ".pre-commit-config.yaml").exists()

            # 2. Hook is in the file
            assert "deptry" in hook_names

            # 3. Test file contents
            assert (uv_init_repo_dir / ".pre-commit-config.yaml").read_text() == (
                """\
repos:
  - repo: local
    hooks:
      - id: deptry
        name: deptry
        always_run: true
        entry: uv run --frozen deptry src
        language: system
"""
            )

            # 4. Check messages
            out, _ = capfd.readouterr()
            assert out == (
                "✔ Adding 'deptry' to the 'dev' dependency group.\n"
                "✔ Adding hook 'deptry' to '.pre-commit-config.yaml'.\n"
                "☐ Call the 'deptry src' command to run deptry.\n"
            )

        def test_placeholder_removed(
            self,
            uv_init_repo_dir: Path,
            capfd: pytest.CaptureFixture[str],
            vary_network_conn: None,
        ):
            # Arrange
            (uv_init_repo_dir / ".pre-commit-config.yaml").write_text(
                """\
repos:
  - repo: local
    hooks:
      - id: placeholder
"""
            )

            # Act
            with change_cwd(uv_init_repo_dir):
                use_deptry()

            # Assert
            contents = (uv_init_repo_dir / ".pre-commit-config.yaml").read_text()
            assert "deptry" in contents
            assert "placeholder" not in contents
            out, err = capfd.readouterr()
            assert not err
            # Expecting not to get a specific message about removing the placeholder.
            assert out == (
                "✔ Adding 'deptry' to the 'dev' dependency group.\n"
                "✔ Adding hook 'deptry' to '.pre-commit-config.yaml'.\n"
                "☐ Call the 'deptry src' command to run deptry.\n"
            )

        def test_remove(
            self, uv_init_repo_dir: Path, capfd: pytest.CaptureFixture[str]
        ):
            # Arrange
            with change_cwd(uv_init_repo_dir), usethis_config.set(quiet=True):
                use_deptry()
                use_pre_commit()
                content = (uv_init_repo_dir / ".pre-commit-config.yaml").read_text()
                assert "deptry" in content

            # Act
            with change_cwd(uv_init_repo_dir):
                use_deptry(remove=True)

            # Assert
            content = (uv_init_repo_dir / ".pre-commit-config.yaml").read_text()
            assert "deptry" not in content


class TestPreCommit:
    class TestUse:
        def test_fresh(
            self,
            uv_init_repo_dir: Path,
            capfd: pytest.CaptureFixture[str],
            vary_network_conn: None,
        ):
            # Act
            with change_cwd(uv_init_repo_dir):
                use_pre_commit()

                # Assert
                # Has dev dep
                (dev_dep,) = get_deps_from_group("dev")
                assert dev_dep == "pre-commit"
            # Correct stdout
            out, _ = capfd.readouterr()
            assert out == (
                "✔ Adding 'pre-commit' to the 'dev' dependency group.\n"
                "✔ Writing '.pre-commit-config.yaml'.\n"
                "✔ Adding placeholder hook to '.pre-commit-config.yaml'.\n"
                "☐ Remove the placeholder hook in '.pre-commit-config.yaml'.\n"
                "☐ Replace it with your own hooks.\n"
                "☐ Alternatively, use 'usethis tool' to add other tools and their hooks.\n"
                "✔ Ensuring pre-commit hooks are installed.\n"
                "☐ Call the 'pre-commit run --all-files' command to run the hooks manually.\n"
            )
            # Config file
            assert (uv_init_repo_dir / ".pre-commit-config.yaml").exists()
            contents = (uv_init_repo_dir / ".pre-commit-config.yaml").read_text()
            assert contents == (
                """\
repos:
  - repo: local
    hooks:
      - id: placeholder
        name: Placeholder - add your own hooks!
        entry: uv run python -c "print('hello world!')"
        language: system
"""
            )

        def test_already_exists(self, uv_init_repo_dir: Path, vary_network_conn: None):
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
                use_pre_commit()

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

        def test_bad_commit(self, uv_init_repo_dir: Path, vary_network_conn: None):
            # Act
            with change_cwd(uv_init_repo_dir):
                use_pre_commit()
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

    class TestRemove:
        def test_config_file(self, uv_init_repo_dir: Path, vary_network_conn: None):
            # Arrange
            (uv_init_repo_dir / ".pre-commit-config.yaml").touch()

            # Act
            with change_cwd(uv_init_repo_dir):
                use_pre_commit(remove=True)

            # Assert
            assert not (uv_init_repo_dir / ".pre-commit-config.yaml").exists()

        def test_dep(self, uv_init_repo_dir: Path, vary_network_conn: None):
            with change_cwd(uv_init_repo_dir):
                # Arrange
                add_deps_to_group(["pre-commit"], "dev")

                # Act
                use_pre_commit(remove=True)

                # Assert
                assert not get_deps_from_group("dev")

        def test_stdout(
            self, uv_init_repo_dir: Path, capfd: pytest.CaptureFixture[str]
        ):
            # Arrange
            (uv_init_repo_dir / ".pre-commit-config.yaml").write_text(
                """\
repos:
  - repo: local
    hooks:
      - id: pre-commit
"""
            )

            # Act
            with change_cwd(uv_init_repo_dir):
                use_pre_commit(remove=True)

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert out == (
                "✔ Adding 'pre-commit' to the 'dev' dependency group.\n"
                "✔ Ensuring pre-commit hooks are uninstalled.\n"
                "✔ Removing '.pre-commit-config.yaml'.\n"
                "✔ Removing 'pre-commit' from the 'dev' dependency group.\n"
            )

    class TestBitbucketCIIntegration:
        def test_prexisting(self, uv_init_repo_dir: Path):
            # Arrange
            (uv_init_repo_dir / "bitbucket-pipelines.yml").write_text(
                """\
image: atlassian/default-image:3
"""
            )

            with change_cwd(uv_init_repo_dir):
                # Act
                use_pre_commit()

            # Assert
            contents = (uv_init_repo_dir / "bitbucket-pipelines.yml").read_text()
            assert "pre-commit" in contents

        def test_remove(
            self, uv_init_repo_dir: Path, capfd: pytest.CaptureFixture[str]
        ):
            # Arrange
            with change_cwd(uv_init_repo_dir), usethis_config.set(quiet=True):
                use_pre_commit()
            (uv_init_repo_dir / "bitbucket-pipelines.yml").write_text(
                """\
image: atlassian/default-image:3
pipelines:
    default:
      - step:
            name: Run pre-commit
            script:
              - echo "Hello, World!"
"""
            )

            # Act
            with change_cwd(uv_init_repo_dir):
                use_pre_commit(remove=True)

            # Assert
            contents = (uv_init_repo_dir / "bitbucket-pipelines.yml").read_text()
            assert (
                contents
                == """\
image: atlassian/default-image:3
definitions:
    caches:
        uv: ~/.cache/uv
    script_items:
      - &install-uv |
        curl -LsSf https://astral.sh/uv/install.sh | sh
        source $HOME/.local/bin/env
        export UV_LINK_MODE=copy
        uv --version
pipelines:
    default:
      - step:
            name: Placeholder - add your own steps!
            caches:
              - uv
            script:
              - *install-uv
              - echo 'Hello, world!'
"""
            )
            out, err = capfd.readouterr()
            assert not err
            assert out == (
                "✔ Removing pre-commit step from 'bitbucket-pipelines.yml'.\n"
                "✔ Adding cache 'uv' definition to 'bitbucket-pipelines.yml'.\n"
                "✔ Ensuring pre-commit hooks are uninstalled.\n"
                "✔ Removing '.pre-commit-config.yaml'.\n"
                "✔ Removing 'pre-commit' from the 'dev' dependency group.\n"
            )


class TestPyprojectFmt:
    class TestAdd:
        class TestPyproject:
            def test_added(
                self,
                uv_init_dir: Path,
                capfd: pytest.CaptureFixture[str],
                vary_network_conn: None,
            ):
                # Arrange
                with change_cwd(uv_init_dir), usethis_config.set(quiet=True):
                    add_deps_to_group(["pyproject-fmt"], "dev")
                content = (uv_init_dir / "pyproject.toml").read_text()

                # Act
                with change_cwd(uv_init_dir):
                    use_pyproject_fmt()

                # Assert
                assert (
                    uv_init_dir / "pyproject.toml"
                ).read_text() == content + "\n" + (
                    """\
[tool.pyproject-fmt]
keep_full_version = true
"""
                )
                out, _ = capfd.readouterr()
                assert out == (
                    "✔ Adding pyproject-fmt config to 'pyproject.toml'.\n"
                    "☐ Call the 'pyproject-fmt pyproject.toml' command to run pyproject-fmt.\n"
                )

        class TestDeps:
            def test_added(
                self,
                uv_init_dir: Path,
                capfd: pytest.CaptureFixture[str],
                vary_network_conn: None,
            ):
                with change_cwd(uv_init_dir):
                    # Act
                    use_pyproject_fmt()

                    # Assert
                    assert get_deps_from_group("dev") == ["pyproject-fmt"]
                out, _ = capfd.readouterr()
                assert out == (
                    "✔ Adding 'pyproject-fmt' to the 'dev' dependency group.\n"
                    "✔ Adding pyproject-fmt config to 'pyproject.toml'.\n"
                    "☐ Call the 'pyproject-fmt pyproject.toml' command to run pyproject-fmt.\n"
                )

    class TestRemove:
        def test_config_file(self, uv_init_dir: Path, vary_network_conn: None):
            # Arrange
            (uv_init_dir / "pyproject.toml").write_text(
                """\
[tool.pyproject-fmt]
foo = "bar"
"""
            )

            # Act
            with change_cwd(uv_init_dir):
                use_pyproject_fmt(remove=True)

            # Assert
            assert (uv_init_dir / "pyproject.toml").read_text() == ""

    class TestPreCommitIntegration:
        def test_use_first(
            self,
            uv_init_repo_dir: Path,
            vary_network_conn: None,
        ):
            with change_cwd(uv_init_repo_dir):
                # Arrange
                use_pre_commit()

                # Act
                use_pyproject_fmt()

                # Assert
                hook_names = get_hook_names()

            assert (uv_init_repo_dir / ".pre-commit-config.yaml").exists()
            assert "pyproject-fmt" in hook_names

        def test_use_after(
            self,
            uv_init_repo_dir: Path,
            vary_network_conn: None,
        ):
            with change_cwd(uv_init_repo_dir):
                # Arrange
                use_pyproject_fmt()

                # Act
                use_pre_commit()

                # Assert
                hook_names = get_hook_names()

            assert (uv_init_repo_dir / ".pre-commit-config.yaml").exists()
            assert "pyproject-fmt" in hook_names

        def test_remove(
            self,
            uv_init_repo_dir: Path,
            capfd: pytest.CaptureFixture[str],
            vary_network_conn: None,
        ):
            with change_cwd(uv_init_repo_dir):
                # Arrange
                with usethis_config.set(quiet=True):
                    use_pyproject_fmt()
                    use_pre_commit()

                # Act
                use_pyproject_fmt(remove=True)

            # Assert
            contents = (uv_init_repo_dir / ".pre-commit-config.yaml").read_text()
            assert "pyproject-fmt" not in contents
            out, err = capfd.readouterr()
            assert not err
            assert out == (
                "✔ Removing pyproject-fmt config from 'pyproject.toml'.\n"
                "✔ Removing pyproject-fmt config from '.pre-commit-config.yaml'.\n"
                "✔ Removing 'pyproject-fmt' from the 'dev' dependency group.\n"
            )


class TestPytest:
    class TestAdd:
        def test_dep(self, uv_init_dir: Path, vary_network_conn: None):
            with change_cwd(uv_init_dir):
                use_pytest()

                assert {
                    "pytest",
                    "pytest-cov",
                    "coverage",
                } <= set(get_deps_from_group("test"))

        def test_bitbucket_integration(self, uv_init_dir: Path, vary_network_conn):
            with change_cwd(uv_init_dir):
                # Arrange
                use_ci_bitbucket()

                # Act
                use_pytest()

            # Assert
            assert "pytest" in (uv_init_dir / "bitbucket-pipelines.yml").read_text()

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
                    use_pytest(remove=True)

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
                    use_pytest(remove=True)

                # Assert
                out, _ = capfd.readouterr()
                assert out == ("✔ Disabling ruff rule 'PT' in 'pyproject.toml'.\n")

        class TestPyproject:
            def test_removed(
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
                    use_pytest(remove=True)

                # Assert
                assert (uv_init_dir / "pyproject.toml").read_text() == ""
                out, _ = capfd.readouterr()
                # N.B. we don't put `pytest` in quotes because we are referring to the
                # tool, not the package.
                assert out == "✔ Removing pytest config from 'pyproject.toml'.\n"

        class TestDependencies:
            def test_removed(self, uv_init_dir: Path):
                with change_cwd(uv_init_dir):
                    # Arrange
                    add_deps_to_group(["pytest"], "test")

                    # Act
                    use_pytest(remove=True)

                    # Assert
                    assert not get_deps_from_group("test")

        class TestBitbucketIntegration:
            def test_remove(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
                # Arrange
                with change_cwd(uv_init_dir), usethis_config.set(quiet=True):
                    use_pytest()

                (uv_init_dir / "bitbucket-pipelines.yml").write_text(
                    """\
image: atlassian/default-image:3
pipelines:
    default:
      - step:
            name: Test - Python 3.12
            script:
              - uv run --python 3.12 pytest
"""
                )

                # Act
                with change_cwd(uv_init_dir):
                    use_pytest(remove=True)

                # Assert
                out, err = capfd.readouterr()
                assert not err
                assert out == (
                    "✔ Removing pytest steps from 'bitbucket-pipelines.yml'.\n"
                    "✔ Adding cache 'uv' definition to 'bitbucket-pipelines.yml'.\n"
                    "✔ Removing pytest config from 'pyproject.toml'.\n"
                    "✔ Removing 'pytest' from the 'test' dependency group.\n"
                    "✔ Removing 'pytest-cov' from the 'test' dependency group.\n"
                    "✔ Removing 'coverage' from the 'test' dependency group.\n"
                    "✔ Removing '/tests'.\n"
                )
                contents = (uv_init_dir / "bitbucket-pipelines.yml").read_text()
                assert (
                    contents
                    == """\
image: atlassian/default-image:3
definitions:
    caches:
        uv: ~/.cache/uv
    script_items:
      - &install-uv |
        curl -LsSf https://astral.sh/uv/install.sh | sh
        source $HOME/.local/bin/env
        export UV_LINK_MODE=copy
        uv --version
pipelines:
    default:
      - step:
            name: Placeholder - add your own steps!
            caches:
              - uv
            script:
              - *install-uv
              - echo 'Hello, world!'
"""
                )


class TestRuff:
    class TestAdd:
        def test_dependency_added(self, uv_init_dir: Path, vary_network_conn: None):
            # Act
            with change_cwd(uv_init_dir):
                use_ruff()

                # Assert
                (dev_dep,) = get_deps_from_group("dev")
            assert dev_dep == "ruff"

        def test_stdout(
            self,
            uv_init_dir: Path,
            capfd: pytest.CaptureFixture[str],
            vary_network_conn: None,
        ):
            # Act
            with change_cwd(uv_init_dir):
                use_ruff()

            # Assert
            out, _ = capfd.readouterr()
            assert out == (
                "✔ Adding 'ruff' to the 'dev' dependency group.\n"
                "✔ Adding ruff config to 'pyproject.toml'.\n"
                "✔ Enabling ruff rules 'A', 'C4', 'E4', 'E7', 'E9', 'F', 'FURB', 'I', 'PLE', \n'PLR', 'RUF', 'SIM', 'UP' in 'pyproject.toml'.\n"
                "☐ Call the 'ruff check --fix' command to run the ruff linter with autofixes.\n"
                "☐ Call the 'ruff format' command to run the ruff formatter.\n"
            )

        def test_pre_commit_first(
            self,
            uv_init_repo_dir: Path,
            capfd: pytest.CaptureFixture[str],
            vary_network_conn: None,
        ):
            # Act
            with change_cwd(uv_init_repo_dir):
                use_ruff()
                use_pre_commit()

                # Assert
                hook_names = get_hook_names()

            assert "ruff-format" in hook_names
            assert "ruff" in hook_names

    class TestRemove:
        def test_config_file(self, uv_init_dir: Path, vary_network_conn: None):
            # Arrange
            (uv_init_dir / "pyproject.toml").write_text(
                """\
[tool.ruff.lint]
select = ["A", "B", "C"]
"""
            )

            # Act
            with change_cwd(uv_init_dir):
                use_ruff(remove=True)

            # Assert
            assert (uv_init_dir / "pyproject.toml").read_text() == ""

        def test_blank_slate(self, uv_init_dir: Path, vary_network_conn: None):
            # Arrange
            contents = (uv_init_dir / "pyproject.toml").read_text()

            # Act
            with change_cwd(uv_init_dir):
                use_ruff(remove=True)

            # Assert
            assert (uv_init_dir / "pyproject.toml").read_text() == contents

        def test_roundtrip(self, uv_init_dir: Path, vary_network_conn: None):
            # Arrange
            contents = (uv_init_dir / "pyproject.toml").read_text()

            # Act
            with change_cwd(uv_init_dir):
                use_ruff()
                use_ruff(remove=True)

            # Assert
            assert (
                (uv_init_dir / "pyproject.toml").read_text()
                == contents
                + """\

[dependency-groups]
dev = []

"""
            )

    class TestPrecommitIntegration:
        def test_use_first(
            self,
            uv_init_repo_dir: Path,
            vary_network_conn: None,
        ):
            with change_cwd(uv_init_repo_dir):
                # Arrange
                use_ruff()

                # Act
                use_pre_commit()

                # Assert
                hook_names = get_hook_names()

            assert "ruff-format" in hook_names
            assert "ruff" in hook_names

        def test_use_after(
            self,
            uv_init_repo_dir: Path,
            vary_network_conn: None,
        ):
            with change_cwd(uv_init_repo_dir):
                # Arrange
                use_pre_commit()

                # Act
                use_ruff()

                # Assert
                hook_names = get_hook_names()

            assert "ruff-format" in hook_names
            assert "ruff" in hook_names

        def test_remove(
            self,
            uv_init_repo_dir: Path,
            capfd: pytest.CaptureFixture[str],
            vary_network_conn: None,
        ):
            with change_cwd(uv_init_repo_dir):
                # Arrange
                with usethis_config.set(quiet=True):
                    use_ruff()
                    use_pre_commit()

                # Act
                use_ruff(remove=True)

            # Assert
            contents = (uv_init_repo_dir / ".pre-commit-config.yaml").read_text()
            assert "ruff" not in contents
            out, err = capfd.readouterr()
            assert not err
            assert out == (
                "✔ Removing ruff-format config from '.pre-commit-config.yaml'.\n"
                "✔ Removing ruff config from '.pre-commit-config.yaml'.\n"
                "✔ Removing ruff config from 'pyproject.toml'.\n"
                "✔ Removing 'ruff' from the 'dev' dependency group.\n"
            )
