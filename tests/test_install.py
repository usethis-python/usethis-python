import shutil
from pathlib import Path

import pytest

from _test import change_cwd
from usethis._backend.uv.call import call_uv_subprocess
from usethis._config import usethis_config
from usethis._config_file import files_manager
from usethis._subprocess import call_subprocess

# The files needed to build the usethis wheel (plus src)
_BUILD_FILES = ("pyproject.toml", "README.md", "LICENSE")


@pytest.fixture(scope="session")
def _usethis_source_dir(
    tmp_path_factory: pytest.TempPathFactory, usethis_dev_dir: Path
) -> Path:
    """A git repo with a copy of the files needed to build the current usethis.

    This is a copy to avoid interacting with pytest.
    """
    source_dir = tmp_path_factory.mktemp("usethis-python")

    for name in _BUILD_FILES:
        shutil.copy2(usethis_dev_dir / name, source_dir / name)
    shutil.copytree(
        usethis_dev_dir / "src",
        source_dir / "src",
        ignore=shutil.ignore_patterns("__pycache__"),
        symlinks=True,
    )

    # Initialize a git repository so the package can be built (since it relies on vcs)
    call_subprocess(["git", "init"], cwd=source_dir)
    call_subprocess(["git", "add", "."], cwd=source_dir)
    call_subprocess(["git", "commit", "-m", "Initial commit"], cwd=source_dir)

    return source_dir


@pytest.fixture
def usethis_installed_dir(uv_init_dir: Path, _usethis_source_dir: Path) -> Path:
    with change_cwd(uv_init_dir), files_manager():
        # Install usethis in a virtual environment
        call_uv_subprocess(
            ["add", f"{_usethis_source_dir.as_posix()}"], change_toml=True
        )

    return uv_init_dir


class TestInstalledInOwnVenv:
    def test_help(self, usethis_installed_dir: Path):
        with change_cwd(usethis_installed_dir):
            # Should run without error
            call_subprocess(["usethis", "--help"])

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_add_pytest(self, usethis_installed_dir: Path):
        with change_cwd(usethis_installed_dir):
            # Should run without error
            if not usethis_config.offline:
                call_subprocess(["usethis", "tool", "pytest"])
            else:
                call_subprocess(["usethis", "tool", "pytest", "--offline"])
