from collections.abc import Generator
from enum import Enum
from pathlib import Path

import pytest
from git import Repo

from usethis._config import usethis_config
from usethis._integrations.uv.call import call_uv_subprocess
from usethis._test import change_cwd, is_offline


@pytest.fixture
def uv_init_dir(tmp_path: Path) -> Path:
    with change_cwd(tmp_path):
        call_uv_subprocess(["init", "--lib"])
    return tmp_path


@pytest.fixture
def uv_init_repo_dir(tmp_path: Path) -> Path:
    with change_cwd(tmp_path):
        call_uv_subprocess(["init", "--lib"])
    Repo.init(tmp_path)
    return tmp_path


class NetworkConn(Enum):
    OFFLINE = 0
    ONLINE = 1


@pytest.fixture(
    params=[
        NetworkConn.ONLINE,  # Run online first since we want to populate caches
        NetworkConn.OFFLINE,
    ],
)
def vary_network_conn(request: pytest.FixtureRequest) -> Generator[bool, None, None]:
    """Fixture to vary the network connection; returns True if offline."""
    if request.param is NetworkConn.ONLINE and is_offline():
        pytest.skip("Network connection is offline")

    offline = request.param is NetworkConn.OFFLINE

    usethis_config.offline = offline
    yield offline
    usethis_config.offline = False
