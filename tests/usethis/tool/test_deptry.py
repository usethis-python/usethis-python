import os
import subprocess
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

import pytest
import tomlkit
from pydantic import TypeAdapter

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


@pytest.fixture
def uv_init_dir(tmp_path: Path) -> None:
    subprocess.run(["uv", "init"], cwd=tmp_path, check=True)
    return tmp_path


class TestDeptry:
    def test_dependency_added(self, uv_init_dir: Path):
        # Act
        with change_cwd(uv_init_dir):
            deptry()

        # Assert
        (dev_dep,) = _get_dev_deps(uv_init_dir)
        assert dev_dep.startswith("deptry>=")

    def test_stdout(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
        # Act
        with change_cwd(uv_init_dir):
            deptry()

        # Assert
        out, _ = capfd.readouterr()
        assert out == "✔ Adding deptry as a development dependency\n"


def _get_dev_deps(proj_dir: Path) -> list[str]:
    pyproject = tomlkit.parse((proj_dir / "pyproject.toml").read_text())
    dev_deps = pyproject["tool"]["uv"]["dev-dependencies"]
    return TypeAdapter(list[str]).validate_python(dev_deps)
