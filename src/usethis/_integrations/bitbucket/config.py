from pathlib import Path

from usethis._console import tick_print

_YAML_CONTENTS = """\
image: atlassian/default-image:3
definitions:
    caches:
        uv: ~/.cache/uv
    scripts:
      - script: &install-uv |-
            curl -LsSf https://astral.sh/uv/install.sh | sh
            source $HOME/.local/env
            export UV_LINK_MODE=copy
            uv --version
pipelines:
    default:
      - step:
            name: Placeholder - add your own steps!
            caches:
              - uv
            script:
              - *install-uv
              - echo 'Hello, world!'
"""


def add_bitbucket_pipeline_config() -> None:
    """Add a Bitbucket pipeline configuration.

    Note that the pipeline is empty and will need steps added to it to run successfully.
    """
    if (Path.cwd() / "bitbucket-pipelines.yml").exists():
        # Early exit; the file already exists
        return

    tick_print("Writing 'bitbucket-pipelines.yml'.")
    yaml_contents = _YAML_CONTENTS

    (Path.cwd() / "bitbucket-pipelines.yml").write_text(yaml_contents)


def remove_bitbucket_pipeline_config() -> None:
    if not (Path.cwd() / "bitbucket-pipelines.yml").exists():
        # Early exit; the file already doesn't exist
        return

    tick_print("Removing 'bitbucket-pipelines.yml' file.")
    (Path.cwd() / "bitbucket-pipelines.yml").unlink()
