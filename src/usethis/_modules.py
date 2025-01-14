import pkgutil
from pathlib import Path


def get_module_names(path: Path) -> list[str]:
    """Get Python modules (either files or subpackages) in a directory."""
    return [name for _, name, _ in pkgutil.iter_modules([path.as_posix()])]
