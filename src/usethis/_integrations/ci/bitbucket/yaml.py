from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import ValidationError

from usethis._integrations.ci.bitbucket.errors import BitbucketPipelinesYAMLSchemaError
from usethis._integrations.ci.bitbucket.schema import (
    PipelinesConfiguration,
    Step,
    Step2,
    StepBase,
)
from usethis._integrations.file.yaml.io_ import YAMLFileManager
from usethis._integrations.file.yaml.update import update_ruamel_yaml_map
from usethis._integrations.pydantic.dump import fancy_model_dump

if TYPE_CHECKING:
    from pydantic import BaseModel

    from usethis._integrations.pydantic.dump import ModelRepresentation

ORDER_BY_CLS: dict[type[BaseModel], list[str]] = {
    PipelinesConfiguration: ["image", "clone", "definitions"],
    StepBase: ["name", "caches", "script"],
    Step: ["name", "caches", "script"],
    Step2: ["name", "caches", "script"],
}


class BitbucketPipelinesYAMLManager(YAMLFileManager):
    """Class to manage the bitbucket-pipelines.yml file."""

    @property
    def relative_path(self) -> Path:
        return Path("bitbucket-pipelines.yml")

    def model_validate(self) -> PipelinesConfiguration:
        """Validate the current document content against the JSON schema.

        Returns:
            Validated pydantic model.

        Raises:
            BitbucketPipelinesYAMLConfigError: If validation fails.
        """
        doc = self.get()
        try:
            return PipelinesConfiguration.model_validate(doc.content)
        except ValidationError as err:
            msg = f"Invalid 'bitbucket-pipelines.yml' file:\n{err}"
            raise BitbucketPipelinesYAMLSchemaError(msg) from None

    def commit_model(self, model: PipelinesConfiguration) -> None:
        doc = self.get()

        # Special handling for script_items: These items may contain YAML anchors (e.g.,
        # &install-uv) which are stored as LiteralScalarString objects in doc.content.
        # Pydantic cannot serialize these objects, so we preserve the original doc.content
        # version rather than using the model's version. To prevent silent data loss, we
        # validate that the model's script_items match doc.content before discarding them.

        # Save script_items from content before update (they have YAML anchors)
        # We may have modified them directly in content, and they should not be
        # overwritten by the model's version (which may be plain strings)
        saved_script_items = None
        if isinstance(doc.content, dict) and "definitions" in doc.content:
            definitions = doc.content["definitions"]
            if isinstance(definitions, dict) and "script_items" in definitions:
                saved_script_items = definitions["script_items"]

        # Validate that model's script_items match doc.content's script_items
        # This ensures we don't silently discard changes
        if model.definitions and model.definitions.script_items:
            model_script_items = model.definitions.script_items

            # Check consistency with doc.content
            if saved_script_items is not None:
                # Compare lengths
                if len(model_script_items) != len(saved_script_items):
                    msg = (
                        f"Script items mismatch: model has {len(model_script_items)} items "
                        f"but doc.content has {len(saved_script_items)} items. "
                        f"This indicates the model was modified independently from doc.content."
                    )
                    raise NotImplementedError(msg)

                # Compare string content (convert both sides to strings for comparison)
                for i, (model_item, content_item) in enumerate(
                    zip(model_script_items, saved_script_items, strict=True)
                ):
                    model_str = str(model_item)
                    content_str = str(content_item)
                    if model_str != content_str:
                        msg = (
                            f"Script item mismatch at index {i}: "
                            f"model has {model_str!r} but doc.content has {content_str!r}. "
                            f"This indicates the model was modified independently from doc.content."
                        )
                        raise NotImplementedError(msg)

            # Save and temporarily remove script_items from model before serialization
            saved_model_script_items = model_script_items
            model.definitions.script_items = None
        else:
            saved_model_script_items = None

        dump = _bitbucket_fancy_dump(model, reference=doc.content)

        # Restore script_items to model
        if saved_model_script_items is not None and model.definitions:
            model.definitions.script_items = saved_model_script_items

        update_ruamel_yaml_map(doc.content, dump, preserve_comments=True)

        # Restore script_items into the updated definitions (preserve YAML anchors)
        if (
            saved_script_items is not None
            and isinstance(doc.content, dict)
            and "definitions" in doc.content
            and isinstance(doc.content["definitions"], dict)
        ):
            doc.content["definitions"]["script_items"] = saved_script_items

        self.model_validate()
        self.commit(doc)


def _bitbucket_fancy_dump(
    config: PipelinesConfiguration, *, reference: ModelRepresentation | None = None
) -> dict[str, ModelRepresentation]:
    dump = fancy_model_dump(config, reference=reference, order_by_cls=ORDER_BY_CLS)

    if not isinstance(dump, dict):
        msg = (
            f"Invalid '{type(config)}' representation when dumping; expected dict, got "
            f"{type(dump)}."
        )
        raise TypeError(msg)

    return dump
