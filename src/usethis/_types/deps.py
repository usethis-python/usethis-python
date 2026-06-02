"""Dependency model definitions."""

from pydantic import BaseModel
from typing_extensions import override


class Dependency(BaseModel):
    name: str
    extras: frozenset[str] = frozenset()
    is_identifying: bool = True
    """Whether the dependency is characteristic of the tool that declares it.

    Supporting dependencies that are shared between tools (e.g. ``tomli``, which
    multiple tools need to read TOML on Python < 3.11) should set this to False so
    that their presence does not, on its own, imply that any particular tool is being
    used. See ``ToolSpec.is_declared_as_dep``.
    """

    @override
    def __str__(self) -> str:
        return self.to_requirement_string()

    @override
    def __eq__(self, other: object) -> bool:
        # Identity is based on name and extras only; is_identifying is metadata that
        # does not affect whether two dependencies refer to the same package.
        if not isinstance(other, Dependency):
            return NotImplemented
        return self.name == other.name and self.extras == other.extras

    @override
    def __hash__(self) -> int:
        return hash((self.__class__.__name__, self.name, self.extras))

    def to_requirement_string(self) -> str:
        """Convert the dependency to a requirements string."""
        extras_str = f"[{','.join(sorted(self.extras))}]" if self.extras else ""
        return f"{self.name}{extras_str}"
