import os
import subprocess
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

import tomlkit

from usethis.tool.deptry import deptry


@contextmanager
def change_cwd(new_dir: Path) -> Generator[None, None, None]:
    """Change the working directory temporarily."""
    old_dir = Path.cwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(old_dir)


class TestDeptry:
    def test_dependency_added(self, tmp_path: Path):
        # Arrange
        subprocess.run(["uv", "init"], cwd=tmp_path, check=True)

        # Act
        with change_cwd(tmp_path):
            deptry()

        # Assert
        pyproject = tomlkit.parse((tmp_path / "pyproject.toml").read_text())
        dev_deps = pyproject["tool"]["uv"]["dev-dependencies"]

        assert len(dev_deps) == 1
        assert dev_deps[0].startswith("deptry>=")
