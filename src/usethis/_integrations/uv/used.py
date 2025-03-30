from pathlib import Path

from usethis._integrations.file.pyproject_toml.io_ import PyprojectTOMLManager


def is_uv_used() -> bool:
    return (
        (Path.cwd() / "uv.lock").exists()
        or (Path.cwd() / "uv.toml").exists()
        or ["tool", "uv"] in PyprojectTOMLManager()
    )
