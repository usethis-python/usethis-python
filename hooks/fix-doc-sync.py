"""Fix sync blocks in markdown files to match their source files.

Scans markdown files for comment pairs of the form:
    <!-- sync:path/to/file -->
    ...content...
    <!-- /sync:path/to/file -->

and replaces the content between the markers with the referenced file's content,
preserving any markdown fenced code block wrapper. Exits with code 1 if any
files were modified (following the pre-commit autofix convention).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Pattern matches <!-- sync:some/path --> and captures the path.
_SYNC_START = re.compile(r"^<!--\s*sync:(\S+)\s*-->$")
# Pattern matches <!-- /sync:some/path --> and captures the path.
_SYNC_END = re.compile(r"^<!--\s*/sync:(\S+)\s*-->$")
# Pattern matches a markdown fenced code block opening (e.g. ```text).
_CODEBLOCK_FENCE = re.compile(r"^```\w*$")


def _detect_codeblock_fence(text: str) -> str:
    """Return the opening fence line if text is wrapped in a code block, else ''."""
    stripped = text.strip()
    lines = stripped.splitlines()
    if (
        len(lines) >= 2
        and _CODEBLOCK_FENCE.match(lines[0])
        and lines[-1].strip() == "```"
    ):
        return lines[0]
    return ""


def _build_replacement(actual_content: str, expected: str) -> str:
    """Build the replacement content for a sync block, preserving code fences."""
    fence = _detect_codeblock_fence(actual_content)
    if fence:
        return f"\n{fence}\n{expected}\n```\n\n"
    return f"\n{expected}\n\n"


def _collect_block(
    lines: list[str], start: int, source_path: str
) -> tuple[list[str], int, bool]:
    """Collect content lines from start until the matching end marker.

    Returns (content_lines, end_index, found_end).
    """
    content_lines: list[str] = []
    idx = start
    while idx < len(lines):
        end_match = _SYNC_END.match(lines[idx].strip())
        if end_match and end_match.group(1) == source_path:
            return content_lines, idx, True
        content_lines.append(lines[idx])
        idx += 1
    return content_lines, idx, False


def _fix_file(path: Path) -> bool:
    """Fix sync blocks in a single file. Returns True if modifications were made."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    new_lines: list[str] = []
    modified = False
    i = 0

    while i < len(lines):
        start_match = _SYNC_START.match(lines[i].strip())
        if not start_match:
            new_lines.append(lines[i])
            i += 1
            continue

        # Found a sync start marker.
        source_path_str = start_match.group(1)
        new_lines.append(lines[i])  # Keep the start marker line.
        i += 1

        content_lines, end_idx, found_end = _collect_block(lines, i, source_path_str)

        if not found_end:
            new_lines.extend(content_lines)
            i = end_idx
            print(
                f"ERROR: No closing marker found for sync:{source_path_str}",
                file=sys.stderr,
            )
            continue

        source = Path(source_path_str)
        if not source.is_file():
            new_lines.extend(content_lines)
            new_lines.append(lines[end_idx])
            i = end_idx + 1
            print(
                f"ERROR: Source file {source} referenced in {path} not found.",
                file=sys.stderr,
            )
            continue

        expected = source.read_text(encoding="utf-8").strip()
        actual_content = "".join(content_lines)
        replacement = _build_replacement(actual_content, expected)

        if actual_content != replacement:
            modified = True
            new_lines.extend(replacement.splitlines(keepends=True))
        else:
            new_lines.extend(content_lines)

        new_lines.append(lines[end_idx])  # Keep the end marker line.
        i = end_idx + 1

    if modified:
        path.write_text("".join(new_lines), encoding="utf-8")

    return modified


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: fix-doc-sync.py <file> [<file> ...]", file=sys.stderr)
        return 1

    any_modified = False
    failed = False

    for filepath in sys.argv[1:]:
        path = Path(filepath)
        if not path.is_file():
            print(f"ERROR: {path} not found.", file=sys.stderr)
            failed = True
            continue

        was_modified = _fix_file(path)
        if was_modified:
            print(f"Fixed sync blocks in {path}.")
            any_modified = True

    if failed:
        return 1

    if any_modified:
        return 1

    print("All sync blocks are up to date.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
