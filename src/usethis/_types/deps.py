"""Dependency model definitions."""

from pydantic import BaseModel
from typing_extensions import override


class Dependency(BaseModel):
    name: str
    extras: frozenset[str] = frozenset()

    @override
    def __str__(self) -> str:
        return self.to_requirement_string()

    @override
    def __hash__(self) -> int:
        return hash((self.__class__.__name__, self.name, self.extras))

    def to_requirement_string(self) -> str:
        """Convert the dependency to a requirements string."""
        extras_str = f"[{','.join(sorted(self.extras))}]" if self.extras else ""
        return f"{self.name}{extras_str}"
