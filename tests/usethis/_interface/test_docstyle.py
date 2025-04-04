from pathlib import Path

import pytest
import typer

from usethis._interface.docstyle import docstyle
from usethis._test import change_cwd


class TestDocstyle:
    def test_invalid_style(self, capfd: pytest.CaptureFixture[str]):
        with pytest.raises(typer.Exit):
            docstyle("invalid_style")
        out, err = capfd.readouterr()
        assert "Invalid docstring style" in out
        assert not err

    def test_google_runs(self, tmp_path: Path):
        with change_cwd(tmp_path):
            docstyle("google")
