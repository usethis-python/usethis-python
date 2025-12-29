from __future__ import annotations

from usethis.errors import FileConfigError, UsethisError


class UnexpectedImportPipelineError(UsethisError):
    """Raised when an import pipeline is unexpectedly encountered."""


class MissingStepError(ValueError):
    """Raised when a step cannot be found in the pipeline."""


class BitbucketPipelinesYAMLSchemaError(FileConfigError):
    """Raised when there the 'bitbucket-pipelines.yml' file does not conform to the expected schema."""

    @property
    def name(self) -> str:
        """The name of the file that has a configuration error."""
        return "bitbucket-pipelines.yml"
