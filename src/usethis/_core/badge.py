import re
from pathlib import Path

from usethis._console import tick_print

RUFF_MARKDOWN = "[![Ruff](<https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json>)](<https://github.com/astral-sh/ruff>)"
PRECOMMIT_MARKDOWN = "[![pre-commit](<https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit>)](<https://github.com/pre-commit/pre-commit>)"

MARKDOWN_ORDER = [
    RUFF_MARKDOWN,
    PRECOMMIT_MARKDOWN,
]


def add_ruff_badge():
    add_badge(markdown=RUFF_MARKDOWN, badge_name="ruff")


def add_badge(markdown: str, badge_name: str) -> None:
    path = Path.cwd() / "README.md"

    if not path.exists():
        raise NotImplementedError

    predecessors = []
    for _m in MARKDOWN_ORDER:
        if _m == markdown:
            break
        predecessors.append(_m)

    content = path.read_text()

    original_lines = content.splitlines()

    have_added = False
    lines: list[str] = []
    for original_line in original_lines:
        if original_line.strip() == markdown:
            # The file can be left alone - the badge is already there
            return

        if (
            not have_added
            and original_line.strip() not in predecessors
            and not is_blank(original_line)
            and not is_header(original_line)
        ):
            tick_print(f"Adding {badge_name} badge to 'README.md'.")
            lines.append(markdown)
            have_added = True

            # Protect the badge we've just added
            if not is_blank(original_line) and not is_badge(original_line):
                lines.append("")

        lines.append(original_line)

    # In case the badge needs to go at the bottom of the file
    if not have_added:
        # Add a blank line between headers and the badge
        if original_lines and is_header(original_lines[-1]):
            lines.append("")
        tick_print(f"Adding {badge_name} badge to 'README.md'.")
        lines.append(markdown)

    # If the first line is blank, we basically just want to replace it.
    if is_blank(lines[0]):
        del lines[0]

    # Ensure final newline
    if lines[-1] != "":
        lines.append("")

    path.write_text("\n".join(lines))


def is_blank(line: str) -> bool:
    return line.isspace() or not line


def is_header(line: str) -> bool:
    return line.strip().startswith("#")


def is_badge(line: str) -> bool:
    # A heuristic
    return (
        re.match(r"^\[!\[.*\]\(.*\)\]\(.*\)$", line) is not None
        or re.match(r"^\!\[.*\]\(.*\)$", line) is not None
    )
