import re
from pathlib import Path
from typing import Self

from pydantic import BaseModel

from usethis._console import tick_print
from usethis._core.readme import add_readme


class Badge(BaseModel):
    markdown: str

    @property
    def name(self) -> str | None:
        match = re.match(r"^\s*\[!\[(.*)\]\(.*\)\]\(.*\)\s*$", self.markdown)
        if match:
            return match.group(1)
        match = re.match(r"^\s*\!\[(.*)\]\(.*\)\s*$", self.markdown)
        if match:
            return match.group(1)
        return None

    def equivalent_to(self, other: Self) -> bool:
        return self.name == other.name


RUFF_BADGE = Badge(
    markdown="[![Ruff](<https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json>)](<https://github.com/astral-sh/ruff>)"
)
PRE_COMMIT_BADGE = Badge(
    markdown="[![pre-commit](<https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit>)](<https://github.com/pre-commit/pre-commit>)"
)

BADGE_ORDER = [
    RUFF_BADGE,
    PRE_COMMIT_BADGE,
]


def add_ruff_badge():
    add_badge(RUFF_BADGE)


def add_pre_commit_badge():
    add_badge(PRE_COMMIT_BADGE)


def remove_ruff_badge():
    remove_badge(RUFF_BADGE)


def remove_pre_commit_badge():
    remove_badge(PRE_COMMIT_BADGE)


def add_badge(badge: Badge) -> None:
    path = Path.cwd() / "README.md"

    if not path.exists():
        add_readme()

    prerequisites: list[Badge] = []
    for _b in BADGE_ORDER:
        if badge.equivalent_to(_b):
            break
        prerequisites.append(_b)

    content = path.read_text()

    original_lines = content.splitlines()

    have_added = False
    have_encountered_badge = False
    html_h1_count = 0
    lines: list[str] = []
    for original_line in original_lines:
        if is_badge(original_line):
            have_encountered_badge = True

        html_h1_count += _count_h1_open_tags(original_line)
        in_block = html_h1_count > 0
        html_h1_count -= _count_h1_close_tags(original_line)

        original_badge = Badge(markdown=original_line)

        if original_badge.equivalent_to(badge):
            # If the badge is already there, we don't need to do anything
            return

        original_line_is_prerequisite = any(
            original_badge.equivalent_to(prerequisite) for prerequisite in prerequisites
        )
        if not have_added and (
            not original_line_is_prerequisite
            and (not is_blank(original_line) or have_encountered_badge)
            and not is_header(original_line)
            and not in_block
        ):
            lines.append(badge.markdown)
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
        lines.append(badge.markdown)
        have_added = True

    tick_print(f"Adding {badge.name} badge to 'README.md'.")

    # If the first line is blank, we basically just want to replace it.
    if is_blank(lines[0]):
        del lines[0]

    output = "\n".join(lines)

    # Ensure final newline
    if have_added:
        output = _ensure_final_newline(output)

    path.write_text(output)


def _ensure_final_newline(content: str) -> str:
    if not content or content[-1] != "\n":
        content += "\n"
    return content


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


def _count_h1_open_tags(line: str) -> int:
    h1_start_match = re.match(r"(<h1\s.*>)", line)
    if h1_start_match is not None:
        return len(h1_start_match.groups())
    return 0


def _count_h1_close_tags(line: str) -> int:
    return line.count("</h1>")


def remove_badge(badge: Badge) -> None:
    path = Path.cwd() / "README.md"

    if not path.exists():
        return

    content = path.read_text()

    original_lines = content.splitlines()
    if content.endswith("\n"):
        original_lines.append("")

    lines: list[str] = []
    have_removed = False
    skip_blank = False
    for idx, original_line in enumerate(original_lines):
        if not skip_blank:
            if Badge(markdown=original_line).equivalent_to(badge):
                tick_print(f"Removing {badge.name} badge from 'README.md'.")
                have_removed = True

                # Merge consecutive blank lines around the badges,
                # if there is only one left
                if (
                    idx - 1 >= 0
                    and idx + 1 < len(original_lines)
                    and is_blank(original_lines[idx - 1])
                    and is_blank(original_lines[idx + 1])
                ):
                    skip_blank = True  # i.e. next iteration once we hit a blank

                continue

            lines.append(original_line)
        else:
            skip_blank = False

    output = "\n".join(lines)

    # Ensure final newline
    if have_removed:
        output = _ensure_final_newline(output)

    path.write_text(output)
