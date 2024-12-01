from pydantic import Field, RootModel, ValidationError

from usethis._integrations.bitbucket.io import (
    BitbucketPipelinesYAMLConfigError,
    edit_bitbucket_pipelines_yaml,
)
from usethis._integrations.bitbucket.schema import Definitions, Script
from usethis._integrations.yaml.update import update_ruamel_yaml_map


# It's not in the schema but we want to follow this convention
class ScriptDefinition(RootModel[list[Script]]):
    root: list[Script] = Field(
        ...,
        min_length=1,
    )


def add_script_to_definitions(script: Script, anchor_name: str) -> None:
    """Add an anchorized script definition to a Bitbucket pipeline configuration.

    Note that the definitions.script section is not currently a part of the schema as of
    2024-11-22, although it is valid.
    """
    with edit_bitbucket_pipelines_yaml() as doc:
        config = doc.model

        if config.definitions is None:
            config.definitions = Definitions()

        try:
            scripts = getattr(config.definitions, "scripts")
        except AttributeError:
            scripts = ScriptDefinition([script])
            setattr(config.definitions, "scripts", scripts)
        else:
            try:
                scripts = ScriptDefinition.model_validate(scripts)
            except ValidationError as err:
                msg = (
                    f"Unsupported 'definitions.scripts' configuration in "
                    f"'bitbucket-pipelines.yml' file:\n{err}"
                )
                raise BitbucketPipelinesYAMLConfigError(msg) from None

            scripts.root.append(script)

        update_ruamel_yaml_map(doc.content, config.model_dump(), preserve_comments=True)
