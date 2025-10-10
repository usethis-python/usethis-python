from pathlib import Path


def test_assemble_readme_from_docs(usethis_dev_dir: Path):
    """The README should be kept in-sync with the corresponding doc packages."""

    parts = []

    # Logo
    parts.append("""\
<h1 align="center">
  <img src="https://raw.githubusercontent.com/usethis-python/usethis-python/refs/heads/main/docs/logo.svg"><br>
</h1>
""")

    # Header
    parts.append("""\
# usethis
""")

    # Badges
    parts.append("""\
[![usethis](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/usethis-python/usethis-python/main/assets/badge/v1.json)](https://github.com/usethis-python/usethis-python)
[![PyPI Version](https://img.shields.io/pypi/v/usethis.svg)](https://pypi.python.org/pypi/usethis)
![PyPI License](https://img.shields.io/pypi/l/usethis.svg)
[![PyPI Supported Versions](https://img.shields.io/pypi/pyversions/usethis.svg)](https://pypi.python.org/pypi/usethis)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![codecov](https://codecov.io/gh/usethis-python/usethis-python/graph/badge.svg?token=0QW539GSP9)](https://codecov.io/gh/usethis-python/usethis-python)
[![GitHub Actions Status](https://github.com/usethis-python/usethis-python/workflows/CI/badge.svg)](https://github.com/usethis-python/usethis-python/actions)
[![Docs](https://app.readthedocs.org/projects/usethis/badge/?version=stable)](https://usethis.readthedocs.io/en/stable/)
""")

    # Main sections
    parts.append(
        _get_doc_file(
            usethis_dev_dir / "docs" / "index.md", skip_lines=2, demote_headers=False
        )
    )
    parts.append(_get_doc_file(usethis_dev_dir / "docs" / "getting-started.md"))
    cli_overview_content = _get_doc_file(
        usethis_dev_dir / "docs" / "cli" / "overview.md",
    ).replace(  # README uses absolute links, docs use relative links
        "`](reference.md#",
        "`](https://usethis.readthedocs.io/en/stable/cli/reference#",
    )
    parts.append(cli_overview_content)
    parts.append(_get_doc_file(usethis_dev_dir / "docs" / "example-usage.md"))
    parts.append(_get_doc_file(usethis_dev_dir / "docs" / "similar-projects.md"))

    # Back matter
    parts.append("""\
## 🚀 Development

[![Commits since latest release](https://img.shields.io/github/commits-since/usethis-python/usethis-python/latest.svg)](https://github.com/usethis-python/usethis-python/releases)
[![CodSpeed](https://img.shields.io/endpoint?url=https://codspeed.io/badge.json)](https://codspeed.io/usethis-python/usethis-python)

### Roadmap

Major features planned for later in 2025 are:

- Support for automated GitHub Actions workflows ([#57](https://github.com/usethis-python/usethis-python/issues/57)),
- Support for a typechecker (likely Pyright, [#121](https://github.com/usethis-python/usethis-python/issues/121)), and

Other features are tracked in the [GitHub Issues](https://github.com/usethis-python/usethis-python/issues) page.

### Contributing

See the
[CONTRIBUTING.md](https://github.com/usethis-python/usethis-python/blob/main/CONTRIBUTING.md)
file.

## License

usethis is licensed under the MIT license ([LICENSE](https://github.com/usethis-python/usethis-python/blob/main/LICENSE) or <https://opensource.org/licenses/MIT>)

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in usethis by you, as defined in the Apache License, Version 2.0, (<https://www.apache.org/licenses/LICENSE-2.0>), shall be licensed under the MIT license, without any additional terms or conditions.
""")

    assert (usethis_dev_dir / "README.md").read_text(encoding="utf-8").replace(
        "> [!TIP]\n> ", ""
    ) == "\n".join(parts)


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
