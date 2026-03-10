from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from usethis._types.deps import Dependency

if TYPE_CHECKING:
    from typing_extensions import Self


class DepConfig(BaseModel):
    """Dependency configuration for a tool.

    There is a distinction between managed and unmanaged dependencies. Managed
    dependencies are those which are exclusively managed by one tool, and so can be
    safely added and removed if the tool is added or removed. Unmanaged dependencies are
    those which are not actively added by the tool, but which may have been added
    previously (e.g. by a user or by another version of this tool), and so should only
    be removed and never added.

    Attributes:
        dev_deps: Managed development dependencies.
        test_deps: Managed test dependencies.
        doc_deps: Managed documentation dependencies.
        unmanaged_dev_deps: Unmanaged development dependencies.
        unmanaged_test_deps: Unmanaged test dependencies.
        unmanaged_doc_deps: Unmanaged documentation dependencies.
    """

    dev_deps: list[Dependency] = Field(default_factory=list)
    test_deps: list[Dependency] = Field(default_factory=list)
    doc_deps: list[Dependency] = Field(default_factory=list)
    unmanaged_dev_deps: list[Dependency] = Field(default_factory=list)
    unmanaged_test_deps: list[Dependency] = Field(default_factory=list)
    unmanaged_doc_deps: list[Dependency] = Field(default_factory=list)

    def get_all_dev_deps(self) -> list[Dependency]:
        """Get all (managed and unmanaged) development dependencies."""
        return self.dev_deps + self.unmanaged_dev_deps

    def get_all_test_deps(self) -> list[Dependency]:
        """Get all (managed and unmanaged) test dependencies."""
        return self.test_deps + self.unmanaged_test_deps

    def get_all_doc_deps(self) -> list[Dependency]:
        """Get all (managed and unmanaged) documentation dependencies."""
        return self.doc_deps + self.unmanaged_doc_deps

    @classmethod
    def from_single_dev_dep(cls, dep: Dependency) -> Self:
        """Create a DepConfig with a single managed development dependency."""
        return cls(dev_deps=[dep])

    @classmethod
    def from_single_test_dep(cls, dep: Dependency) -> Self:
        """Create a DepConfig with a single managed test dependency."""
        return cls(test_deps=[dep])

    @classmethod
    def from_single_doc_dep(cls, dep: Dependency) -> Self:
        """Create a DepConfig with a single managed documentation dependency."""
        return cls(doc_deps=[dep])
