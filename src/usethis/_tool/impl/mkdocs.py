from usethis._console import box_print
from usethis._integrations.uv.used import is_uv_used
from usethis._tool.base import Tool


class MkDocsTool(Tool):
    # https://www.mkdocs.org/

    @property
    def name(self) -> str:
        return "MkDocs"

    def print_how_to_use(self) -> None:
        if is_uv_used():
            box_print("Run 'uv run mkdocs build' to build the documentation.")
            box_print("Run 'uv run mkdocs serve' to serve the documentation locally.")
        else:
            box_print("Run 'mkdocs build' to build the documentation.")
            box_print("Run 'mkdocs serve' to serve the documentation locally.")
