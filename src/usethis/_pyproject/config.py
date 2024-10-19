from typing import Any

from pydantic import BaseModel


class PyProjectConfig(BaseModel):
    id_keys: list[str]
    main_contents: dict[str, Any]

    @property
    def contents(self) -> dict[str, Any]:
        c = self.main_contents
        for key in reversed(self.id_keys):
            c = {key: c}
        return c
