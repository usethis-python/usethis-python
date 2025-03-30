from pathlib import Path

import pytest

from usethis._interface.docstyle import docstyle
from usethis._test import change_cwd


class TestDocstyle:
    def test_invalid_style(self):
        with pytest.raises(ValueError, match="Invalid docstring style"):
            docstyle("invalid_style")

    def test_google_runs(self, tmp_path: Path):
        with change_cwd(tmp_path):
            docstyle("google")
