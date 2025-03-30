from typing import Literal

from pydantic import BaseModel

from usethis._core.readme import is_readme_used
from usethis._integrations.ci.bitbucket.used import is_bitbucket_used
from usethis._tool import ALL_TOOLS, RuffTool


class UsageRow(BaseModel):
    category: Literal["tool", "ci", "config", ""]
    name: str
    status: Literal["used", "unused"] | Literal["numpy", "google", "pep257"]


class UsageTable(BaseModel):
    title: str
    rows: list[UsageRow]


def get_usage_table() -> UsageTable:
    """Get the usage table."""
    table = UsageTable(title="Usage", rows=[])

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
