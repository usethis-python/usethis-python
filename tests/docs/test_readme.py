import difflib
from pathlib import Path


def test_assemble_readme_from_docs(usethis_dev_dir: Path):
    """The README should be kept in-sync with the corresponding doc packages."""
    parts = []

    # Main sections
    parts.append(
        _get_doc_file(
            usethis_dev_dir / "docs" / "index.md", skip_lines=2, demote_headers=False
        )
    )
    parts.append(_get_doc_file(usethis_dev_dir / "docs" / "start" / "installation.md"))
    cli_overview_content = _get_doc_file(
        usethis_dev_dir / "docs" / "cli" / "overview.md",
    ).replace(  # README uses absolute links, docs use relative links
        "`](reference.md#",
        "`](https://usethis.readthedocs.io/en/stable/cli/reference#",
    )

    parts.append(cli_overview_content)
    parts.append(
        _get_doc_file(usethis_dev_dir / "docs" / "start" / "example-usage.md")
        .replace(  # README uses absolute links, docs use relative links
            "](detailed-example.md)",
            "](https://usethis.readthedocs.io/en/stable/start/detailed-example)",
        )
        .replace(
            "](../cli/reference.md)",
            "](https://usethis.readthedocs.io/en/stable/cli/reference)",
        )
    )
    parts.append(
        _get_doc_file(usethis_dev_dir / "docs" / "similar-projects.md").replace(
            "](frameworks.md)",
            "](https://usethis.readthedocs.io/en/stable/frameworks)",
        )
    )
    parts.append(_get_doc_file(usethis_dev_dir / "docs" / "about-license.md"))

    content = (
        (usethis_dev_dir / "README.md")
        .read_text(encoding="utf-8")
        .replace("> [!TIP]\n> ", "")
    )
    for part in parts:
        assert part in content, "\n".join(
            difflib.unified_diff(
                part.splitlines(),
                content.splitlines(),
                fromfile="docs",
                tofile="README.md",
                lineterm="",
            )
        )


def _get_doc_file(
    doc_dir: Path, skip_lines: int = 0, demote_headers: bool = True
) -> str:
    content = doc_dir.read_text(encoding="utf-8")
    lines = content.splitlines()[skip_lines:]
    content = "\n".join(lines)
    if demote_headers:
        content = _demote_headers(content)
    return content + "\n"


def _demote_headers(content: str) -> str:
    """Demote all headers in the content by one level.

    Be careful not to touch code in ``` blocks.
    """
    lines = content.splitlines()
    in_block = False

    new_lines = []
    for line in lines:
        if line.startswith("```"):
            in_block = not in_block

        if not in_block:
            line = line.replace("# ", "## ")

        new_lines.append(line)

    return "\n".join(new_lines)
