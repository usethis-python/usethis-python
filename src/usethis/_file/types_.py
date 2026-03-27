"""Shared type aliases for file operations."""

import re
from typing import TypeAlias

Key: TypeAlias = str | re.Pattern[str]
