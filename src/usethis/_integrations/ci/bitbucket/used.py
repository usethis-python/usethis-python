from __future__ import annotations

from pathlib import Path


def is_bitbucket_used() -> bool:
    return (Path.cwd() / "bitbucket-pipelines.yml").exists()
