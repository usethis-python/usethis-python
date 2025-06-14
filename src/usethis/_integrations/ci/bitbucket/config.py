from usethis._config import usethis_config
from usethis._console import tick_print
from usethis._integrations.ci.bitbucket.steps import add_placeholder_step_in_default


def add_bitbucket_pipeline_config(report_placeholder: bool = True) -> None:
    """Add a Bitbucket pipeline configuration.

    Note that the pipeline is empty and will need steps added to it to run successfully.
    """
    if (usethis_config.cpd() / "bitbucket-pipelines.yml").exists():
        # Early exit; the file already exists
        return

    add_placeholder_step_in_default(report_placeholder=report_placeholder)


def remove_bitbucket_pipeline_config() -> None:
    if not (usethis_config.cpd() / "bitbucket-pipelines.yml").exists():
        # Early exit; the file already doesn't exist
        return

    tick_print("Removing 'bitbucket-pipelines.yml'.")
    (usethis_config.cpd() / "bitbucket-pipelines.yml").unlink()
