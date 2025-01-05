from pathlib import Path

from usethis._console import tick_print
from usethis._integrations.bitbucket.steps import (
    add_placeholder_step_in_default,
)


def add_bitbucket_pipeline_config(report_placeholder: bool = True) -> None:
    """Add a Bitbucket pipeline configuration.

    Note that the pipeline is empty and will need steps added to it to run successfully.
    """
    if (Path.cwd() / "bitbucket-pipelines.yml").exists():
        # Early exit; the file already exists
        return

    # TODO wrong place but we need a way of removing the placeholder once it's been
    # added - likewise of removing caches which aren't referenced, and anchorized
    # scripts that aren't referenced.
    # We might be able to get around the weird anchorization attribute-access logic
    # by just directly writing to the CommentedMap etc. with the same list - the
    # ruamel.yaml engine will add the anchor automatically.
    # TODO check the equivalent pre-commit function to make sure this makes sense.
    add_placeholder_step_in_default(report_placeholder=report_placeholder)


def remove_bitbucket_pipeline_config() -> None:
    if not (Path.cwd() / "bitbucket-pipelines.yml").exists():
        # Early exit; the file already doesn't exist
        return

    tick_print("Removing 'bitbucket-pipelines.yml' file.")
    (Path.cwd() / "bitbucket-pipelines.yml").unlink()
