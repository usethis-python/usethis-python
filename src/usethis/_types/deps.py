from pydantic import BaseModel


class Dependency(BaseModel):
    name: str
    extras: frozenset[str] = frozenset()

    def __str__(self) -> str:
        return self.to_requirement_string()

    def __hash__(self) -> int:
        return hash((self.__class__.__name__, self.name, self.extras))

    def to_requirement_string(self) -> str:
        """Convert the dependency to a requirements string."""
        extras_str = f"[{','.join(sorted(self.extras))}]" if self.extras else ""
        return f"{self.name}{extras_str}"
