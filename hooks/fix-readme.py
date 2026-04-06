"""Render README.md from a Jinja2 template and docs sources.

Reads a Jinja2 template, renders it by including content from the docs
directory with appropriate transformations (header demotion, link
replacement, callout wrapping), and writes the result to the output file.
Returns exit code 1 if the file was modified (indicating the change needs
to be committed), 0 otherwise.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import jinja2


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render README.md from a Jinja2 template.",
    )
    parser.add_argument(
        "--template",
        required=True,
        help="Path to the Jinja2 template file.",
    )
    parser.add_argument(
        "--output-file",
        required=True,
        help="Path to the output file to write.",
    )
    args = parser.parse_args()

    template_path = Path(args.template)
    output_file = Path(args.output_file)

    if not template_path.is_file():
        print(f"ERROR: Template {template_path} not found.", file=sys.stderr)
        return 1

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader("."),
        keep_trailing_newline=True,
        undefined=jinja2.StrictUndefined,
        autoescape=jinja2.select_autoescape(),
    )
    env.globals["include_doc"] = _include_doc  # pyright: ignore[reportArgumentType]

    template = env.get_template(template_path.as_posix())
    content = template.render()

    try:
        with open(output_file, encoding="utf-8", newline="") as f:
            existing = f.read()
    except FileNotFoundError:
        existing = None

    modified = content != existing
    if modified:
        output_file.write_text(content, encoding="utf-8", newline="")
        print(f"README updated from template {template_path}.")
    else:
        print("README is already up to date.")

    return 1 if modified else 0


def _demote_headers(content: str) -> str:
    """Demote all markdown headers by one level, respecting fenced code blocks."""
    lines = content.splitlines()
    in_block = False
    new_lines: list[str] = []
    for line in lines:
        if line.startswith("```"):
            in_block = not in_block
        if not in_block:
            line = line.replace("# ", "## ")
        new_lines.append(line)
    return "\n".join(new_lines)


def _include_doc(
    path: str,
    *,
    skip_lines: int = 0,
    demote_headers: bool = True,
    replacements: dict[str, str] | None = None,
    tip_text: str | None = None,
) -> str:
    """Read a doc file and apply transformations.

    Args:
        path: Path to the doc file to include.
        skip_lines: Number of lines to skip from the start of the file.
        demote_headers: Whether to demote markdown headers by one level.
        replacements: Dictionary of string replacements to apply.
        tip_text: If provided, lines starting with this text are wrapped
            in a GitHub `> [!TIP]` callout.
    """
    content = Path(path).read_text(encoding="utf-8")
    lines = content.splitlines()[skip_lines:]
    content = "\n".join(lines)
    if demote_headers:
        content = _demote_headers(content)
    if replacements:
        for old, new in replacements.items():
            content = content.replace(old, new)
    if tip_text:
        lines = content.splitlines()
        new_lines: list[str] = []
        for line in lines:
            if line.startswith(tip_text):
                new_lines.append("> [!TIP]")
                new_lines.append("> " + line)
            else:
                new_lines.append(line)
        content = "\n".join(new_lines)
    return content


if __name__ == "__main__":
    raise SystemExit(main())
