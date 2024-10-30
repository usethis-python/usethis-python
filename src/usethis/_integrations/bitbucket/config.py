from pathlib import Path

from usethis._console import console

_YAML_CONTENTS = """\
image: atlassian/default-image:3

definitions:
  caches:
    uv: ~/.cache/uv
  scripts:
    - script: &install-uv |-
        curl -LsSf https://astral.sh/uv/install.sh | sh
        source $HOME/.cargo/env
        export UV_LINK_MODE=copy
pipelines:
  default: []
"""


def add_bitbucket_pipeline_config() -> None:
    """Add a Bitbucket pipeline configuration.

    Note that the pipeline is empty and will need steps added to it to run successfully.
    """
    if (Path.cwd() / "bitbucket-pipelines.yml").exists():
        # Early exit; the file already exists
        return

    console.tick_print("Writing 'bitbucket-pipelines.yml'.")
    yaml_contents = _YAML_CONTENTS

    (Path.cwd() / "bitbucket-pipelines.yml").write_text(yaml_contents)


def remove_bitbucket_pipeline_config() -> None:
    if not (Path.cwd() / "bitbucket-pipelines.yml").exists():
        # Early exit; the file already doesn't exist
        return

    console.tick_print("Removing 'bitbucket-pipelines.yml' file.")
    (Path.cwd() / "bitbucket-pipelines.yml").unlink()
