"""Check that sync blocks in markdown files match their source files.

Scans markdown files for comment pairs of the form:
    <!-- sync:path/to/file -->
    ...content...
    <!-- /sync:path/to/file -->

and verifies the content between the markers matches the referenced file,
ignoring leading/trailing whitespace differences around the block boundaries.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Pattern matches <!-- sync:some/path --> and captures the path.
_SYNC_START = re.compile(r"^<!--\s*sync:(\S+)\s*-->$")
# Pattern matches <!-- /sync:some/path --> and captures the path.
_SYNC_END = re.compile(r"^<!--\s*/sync:(\S+)\s*-->$")


def _find_sync_blocks(text: str) -> list[tuple[str, str]]:
    """Return (source_path, actual_content) pairs for every sync block."""
    blocks: list[tuple[str, str]] = []
    lines = text.splitlines(keepends=True)
    i = 0
    while i < len(lines):
        start_match = _SYNC_START.match(lines[i].strip())
        if start_match:
            source_path = start_match.group(1)
            content_lines: list[str] = []
            i += 1
            found_end = False
            while i < len(lines):
                end_match = _SYNC_END.match(lines[i].strip())
                if end_match and end_match.group(1) == source_path:
                    found_end = True
                    break
                content_lines.append(lines[i])
                i += 1
            if not found_end:
                print(
                    f"ERROR: No closing marker found for sync:{source_path}",
                    file=sys.stderr,
                )
                blocks.append((source_path, ""))
            else:
                blocks.append((source_path, "".join(content_lines)))
        i += 1
    return blocks


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: check-doc-sync.py <file> [<file> ...]", file=sys.stderr)
        return 1

    failed = False
    for filepath in sys.argv[1:]:
        path = Path(filepath)
        if not path.is_file():
            print(f"ERROR: {path} not found.", file=sys.stderr)
            failed = True
            continue

        text = path.read_text(encoding="utf-8")
        blocks = _find_sync_blocks(text)

        for source_path, actual_content in blocks:
            source = Path(source_path)
            if not source.is_file():
                print(
                    f"ERROR: Source file {source} referenced in {path} not found.",
                    file=sys.stderr,
                )
                failed = True
                continue

            expected = source.read_text(encoding="utf-8")

            if actual_content.strip() != expected.strip():
                print(
                    f"ERROR: Content in {path} between sync:{source_path} markers "
                    f"is out of sync with {source}.",
                    file=sys.stderr,
                )
                failed = True

    if failed:
        return 1

    print("All sync blocks are up to date.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
