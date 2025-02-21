from pathlib import Path
from typing import Literal


def get_source_dir_str() -> Literal["src", "."]:
    src_dir = Path.cwd() / "src"

    if src_dir.exists() and src_dir.is_dir():
        return "src"
    return "."
