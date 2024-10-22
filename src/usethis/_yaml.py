from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import ruamel.yaml
from ruamel.yaml.util import load_yaml_guess_indent


def load_yaml(yaml_path: Path) -> Any:
    yaml = ruamel.yaml.YAML()
    with yaml_path.open(mode="r") as f:
        return yaml.load(f)


@contextmanager
def edit_yaml(yaml_path: Path) -> Generator[Any, None, None]:
    """Change the working directory temporarily."""

    with yaml_path.open(mode="r") as f:
        content, sequence_ind, offset_ind = load_yaml_guess_indent(f)

    yaml = ruamel.yaml.YAML(typ="rt")
    yaml.indent(mapping=sequence_ind, sequence=sequence_ind, offset=offset_ind)

    if content is None:
        content = {}

    yield content

    yaml.dump(content, yaml_path)
