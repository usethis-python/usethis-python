from pydantic import Field, RootModel, ValidationError

from usethis._integrations.bitbucket.io import (
    BitbucketPipelinesYAMLConfigError,
    edit_bitbucket_pipelines_yaml,
)
from usethis._integrations.bitbucket.pipeline import Definitions, Script
from usethis._integrations.yaml.update import update_ruamel_yaml_map


# It's not in the schema but we want to follow this convention
class ScriptDefinition(RootModel[list[Script]]):
    root: list[Script] = Field(
        ...,
        min_length=1,
    )


# TODO not related to this file but need to ensure the tests dir matches the src dir


def add_script_to_definitions(script: Script, anchor_name: str) -> None:
    # TODO need to document that there is a specific format in which the definitions.scripts
    # should be added.
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

            # TODO: can we put it in a canonical order?
            scripts.root.append(script)

        update_ruamel_yaml_map(doc.content, config.model_dump(), preserve_comments=True)
