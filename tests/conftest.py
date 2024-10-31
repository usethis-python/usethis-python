import subprocess
from collections.abc import Generator
from enum import Enum
from pathlib import Path

import pytest
from git import Repo

from usethis._config import usethis_config
from usethis._utils._test import is_offline


@pytest.fixture
def uv_init_dir(tmp_path: Path) -> Path:
    subprocess.run(["uv", "init", "--lib"], cwd=tmp_path, check=True)
    return tmp_path


@pytest.fixture
def uv_init_repo_dir(tmp_path: Path) -> Path:
    subprocess.run(["uv", "init", "--lib"], cwd=tmp_path, check=True)
    Repo.init(tmp_path)
    return tmp_path


class NetworkConn(Enum):
    OFFLINE = 0
    ONLINE = 1


@pytest.fixture(
    params=[
        NetworkConn.OFFLINE,
        NetworkConn.ONLINE,
    ],
)
def vary_network_conn(request: pytest.FixtureRequest) -> Generator[None, None, None]:
    if request.param is NetworkConn.ONLINE and is_offline():
        pytest.skip("Network connection is offline")

    usethis_config.offline = request.param is NetworkConn.OFFLINE
    yield
    usethis_config.offline = False
