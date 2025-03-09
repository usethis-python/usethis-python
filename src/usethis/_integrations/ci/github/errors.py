from __future__ import annotations

from usethis.errors import UsethisError


class GitHubTagError(UsethisError):
    """Custom exception for GitHub tag-related errors."""


class NoGitHubTagsFoundError(GitHubTagError):
    """Custom exception raised when no tags are found."""
