import subprocess
from pathlib import Path

import pytest
from git import Repo


@pytest.fixture
def uv_init_dir(tmp_path: Path) -> Path:
    subprocess.run(["uv", "init", "--lib"], cwd=tmp_path, check=True)
    return tmp_path


@pytest.fixture
def uv_init_repo_dir(tmp_path: Path) -> Path:
    subprocess.run(["uv", "init", "--lib"], cwd=tmp_path, check=True)
    Repo.init(tmp_path)
    return tmp_path
