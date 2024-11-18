import subprocess
from pathlib import Path

import pytest

from usethis._config import usethis_config


class TestDeptry:
    def test_cli(self, uv_init_dir: Path, vary_network_conn: None):
        if not usethis_config.offline:
            subprocess.run(["usethis", "tool", "deptry"], cwd=uv_init_dir, check=True)
        else:
            subprocess.run(
                ["usethis", "tool", "deptry", "--offline"], cwd=uv_init_dir, check=True
            )


class TestPreCommit:
    def test_cli_pass(self, uv_init_repo_dir: Path, vary_network_conn: None):
        if not usethis_config.offline:
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

    def test_cli_fail(self, uv_init_repo_dir: Path, vary_network_conn: None):
        if not usethis_config.offline:
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


class TestRuff:
    def test_cli(self, uv_init_dir: Path, vary_network_conn: None):
        if not usethis_config.offline:
            subprocess.run(["usethis", "tool", "ruff"], cwd=uv_init_dir, check=True)
        else:
            subprocess.run(
                ["usethis", "tool", "ruff", "--offline"],
                cwd=uv_init_dir,
                check=True,
            )
