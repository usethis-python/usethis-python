from pathlib import Path

import pytest

from usethis._config import usethis_config
from usethis._subprocess import SubprocessFailedError, call_subprocess
from usethis._test import change_cwd


class TestDeptry:
    def test_cli(self, uv_init_dir: Path, vary_network_conn: None):
        with change_cwd(uv_init_dir):
            if not usethis_config.offline:
                call_subprocess(["usethis", "tool", "deptry"])
            else:
                call_subprocess(["usethis", "tool", "deptry", "--offline"])


class TestPreCommit:
    def test_cli_pass(self, uv_init_repo_dir: Path, vary_network_conn: None):
        with change_cwd(uv_init_repo_dir):
            if not usethis_config.offline:
                call_subprocess(["usethis", "tool", "pre-commit"])
            else:
                call_subprocess(["usethis", "tool", "pre-commit", "--offline"])

            call_subprocess(["uv", "run", "pre-commit", "run", "--all-files"])

    def test_cli_fail(self, uv_init_repo_dir: Path, vary_network_conn: None):
        with change_cwd(uv_init_repo_dir):
            if not usethis_config.offline:
                call_subprocess(["usethis", "tool", "pre-commit"])
            else:
                call_subprocess(["usethis", "tool", "pre-commit", "--offline"])

            # Pass invalid TOML to fail the pre-commit for validate-pyproject
            (uv_init_repo_dir / "pyproject.toml").write_text("[")
            try:
                call_subprocess(["uv", "run", "pre-commit", "run", "--all-files"])
            except SubprocessFailedError:
                pass
            else:
                pytest.fail("Expected subprocess.CalledProcessError")


class TestRuff:
    def test_cli(self, uv_init_dir: Path, vary_network_conn: None):
        with change_cwd(uv_init_dir):
            if not usethis_config.offline:
                call_subprocess(["usethis", "tool", "ruff"])
            else:
                call_subprocess(["usethis", "tool", "ruff", "--offline"])
