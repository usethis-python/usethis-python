from pathlib import Path


def is_uv_used() -> bool:
    return (Path.cwd() / "uv.lock").exists() or (Path.cwd() / "uv.toml").exists()
