import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator


@contextmanager
def change_cwd(new_dir: Path) -> Generator[None, None, None]:
    """Change the working directory temporarily."""
    old_dir = Path.cwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(old_dir)
