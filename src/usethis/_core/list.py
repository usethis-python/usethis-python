from typing import Literal

from pydantic import BaseModel
from rich.table import Table
from typing_extensions import assert_never

from usethis._console import table_print
from usethis._core.readme import is_readme_used
from usethis._integrations.ci.bitbucket.used import is_bitbucket_used
from usethis._tool.all_ import ALL_TOOLS
from usethis._tool.impl.ruff import RuffTool


class UsageRow(BaseModel):
    category: Literal["tool", "ci", "config", ""]
    name: str
    status: Literal["used", "unused"] | Literal["numpy", "google", "pep257"]

    @property
    def rich_style(self) -> str:
        """Get the Rich style for the row."""
        if self.status in ("used", "numpy", "google", "pep257"):
            return "green"
        elif self.status == "unused":
            return "bright_black"
        else:
            return "white"


class UsageTable(BaseModel):
    rows: list[UsageRow]

    def to_rich(self) -> Table:
        """Convert the table to a rich Table."""
        table = Table(show_lines=True)
        table.add_column("Category", justify="left")
        table.add_column("Name", justify="left")
        table.add_column("Status", justify="left")

        for row in self.rows:
            table.add_row(
                _rich_category(row.category),
                row.name,
                _rich_status(row.status),
                style=row.rich_style,
            )

        return table


def _rich_status(
    status: Literal["used", "unused"] | Literal["numpy", "google", "pep257"],
) -> str:
    """Get richly formatted status."""
    if status == "used":
        return "✔ Used"
    elif status == "unused":
        return "✘ Unused"
    elif status == "numpy":
        return "✔ Numpy"
    elif status == "google":
        return "✔ Google"
    elif status == "pep257":
        return "✔ PEP257"
    else:
        assert_never(status)


def _rich_category(
    category: Literal["tool", "ci", "config", ""],
) -> str:
    """Get richly formatted category."""
    if category == "tool":
        return "[bold]Tool[/bold]"
    elif category == "ci":
        return "[bold]CI[/bold]"
    elif category == "config":
        return "[bold]Config[/bold]"
    elif category == "":
        return "[bold]Other[/bold]"
    else:
        assert_never(category)


def show_usage_table() -> None:
    """Show the usage table."""
    table_print(get_usage_table().to_rich())


def get_usage_table() -> UsageTable:
    """Get the usage table."""
    table = UsageTable(rows=[])

    # Add rows for each tool
    for tool in ALL_TOOLS:
        if tool.is_used():
            table.rows.append(UsageRow(category="tool", name=tool.name, status="used"))
        else:
            table.rows.append(
                UsageRow(category="tool", name=tool.name, status="unused")
            )

    # CI
    if is_bitbucket_used():
        bitbucket_status = "used"
    else:
        bitbucket_status = "unused"
    table.rows.append(
        UsageRow(category="ci", name="Bitbucket Pipelines", status=bitbucket_status)
    )

    # Config
    docstyle_status = RuffTool().get_docstyle()
    if docstyle_status is None:
        docstyle_status = "unused"
    table.rows.append(
        UsageRow(category="config", name="docstyle", status=docstyle_status)
    )

    # Other
    if is_readme_used():
        readme_status = "used"
    else:
        readme_status = "unused"
    table.rows.append(UsageRow(category="", name="README", status=readme_status))

    return table
