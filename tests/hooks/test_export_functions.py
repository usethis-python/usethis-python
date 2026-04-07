"""Tests for hooks/export-functions.py."""

from __future__ import annotations

import importlib.util
import sys
import types
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

# Load the hook module which has a hyphen in its filename.
_HOOK_PATH = Path(__file__).parent.parent.parent / "hooks" / "export-functions.py"
_spec = importlib.util.spec_from_file_location("export_functions", _HOOK_PATH)
assert _spec is not None
assert _spec.loader is not None
_export_functions: types.ModuleType = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_export_functions)

_get_module_public_functions: Callable[..., Any] = getattr(
    _export_functions, "_get_module_public_functions"
)
main: Callable[[], int] = getattr(_export_functions, "main")


class TestGetModulePublicFunctions:
    def test_public_function_with_docstring(self, tmp_path: Path):
        py_file = tmp_path / "mod.py"
        py_file.write_text('def foo():\n    """Do foo."""\n    pass\n')
        result = _get_module_public_functions(py_file)
        assert result == [("foo", "Do foo.")]

    def test_public_function_without_docstring(self, tmp_path: Path):
        py_file = tmp_path / "mod.py"
        py_file.write_text("def foo():\n    pass\n")
        result = _get_module_public_functions(py_file)
        assert result == [("foo", None)]

    def test_private_function_included_by_default(self, tmp_path: Path):
        py_file = tmp_path / "mod.py"
        py_file.write_text('def _bar():\n    """Do bar."""\n    pass\n')
        result = _get_module_public_functions(py_file)
        assert result == [("_bar", "Do bar.")]

    def test_private_function_excluded_with_skip_private(self, tmp_path: Path):
        py_file = tmp_path / "mod.py"
        py_file.write_text('def _bar():\n    """Do bar."""\n    pass\n')
        result = _get_module_public_functions(py_file, skip_private=True)
        assert result == []

    def test_mixed_functions_default(self, tmp_path: Path):
        py_file = tmp_path / "mod.py"
        py_file.write_text(
            'def pub():\n    """Public."""\n    pass\n'
            'def _priv():\n    """Private."""\n    pass\n'
        )
        result = _get_module_public_functions(py_file)
        assert result == [("pub", "Public."), ("_priv", "Private.")]

    def test_mixed_functions_skip_private(self, tmp_path: Path):
        py_file = tmp_path / "mod.py"
        py_file.write_text(
            'def pub():\n    """Public."""\n    pass\n'
            'def _priv():\n    """Private."""\n    pass\n'
        )
        result = _get_module_public_functions(py_file, skip_private=True)
        assert result == [("pub", "Public.")]

    def test_private_function_without_docstring_included_by_default(
        self, tmp_path: Path
    ):
        py_file = tmp_path / "mod.py"
        py_file.write_text("def _bar():\n    pass\n")
        result = _get_module_public_functions(py_file)
        assert result == [("_bar", None)]

    def test_unreadable_file(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]):
        py_file = tmp_path / "missing.py"
        result = _get_module_public_functions(py_file)
        assert result == []
        captured = capsys.readouterr()
        assert "ERROR" in captured.err

    def test_syntax_error_in_file(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ):
        py_file = tmp_path / "bad.py"
        py_file.write_text("def (:\n    pass\n")
        result = _get_module_public_functions(py_file)
        assert result == []
        captured = capsys.readouterr()
        assert "ERROR" in captured.err

    def test_class_methods_not_included(self, tmp_path: Path):
        py_file = tmp_path / "mod.py"
        py_file.write_text(
            'class Foo:\n    def bar(self):\n        """Bar."""\n        pass\n'
        )
        result = _get_module_public_functions(py_file)
        assert result == []

    def test_async_function_included(self, tmp_path: Path):
        py_file = tmp_path / "mod.py"
        py_file.write_text('async def run():\n    """Run."""\n    pass\n')
        result = _get_module_public_functions(py_file)
        assert result == [("run", "Run.")]

    def test_async_private_function_included_by_default(self, tmp_path: Path):
        py_file = tmp_path / "mod.py"
        py_file.write_text('async def _internal():\n    """Internal."""\n    pass\n')
        result = _get_module_public_functions(py_file)
        assert result == [("_internal", "Internal.")]

    def test_async_private_function_excluded_with_skip_private(self, tmp_path: Path):
        py_file = tmp_path / "mod.py"
        py_file.write_text('async def _internal():\n    """Internal."""\n    pass\n')
        result = _get_module_public_functions(py_file, skip_private=True)
        assert result == []

    def test_double_backticks_normalized(self, tmp_path: Path):
        py_file = tmp_path / "mod.py"
        py_file.write_text('def foo():\n    """Use ``bar`` here."""\n    pass\n')
        result = _get_module_public_functions(py_file)
        assert result == [("foo", "Use `bar` here.")]


class TestMain:
    def test_includes_private_by_default(self, tmp_path: Path):
        src = tmp_path / "mypkg"
        src.mkdir()
        (src / "__init__.py").write_text("")
        (src / "mod.py").write_text(
            'def pub():\n    """Public."""\n    pass\n'
            'def _priv():\n    """Private."""\n    pass\n'
        )
        out_file = tmp_path / "out.txt"
        sys.argv = [
            "export-functions.py",
            f"--source-root={src}",
            f"--output-file={out_file}",
        ]
        result = main()
        assert result == 1  # modified
        content = out_file.read_text(encoding="utf-8")
        assert "pub()" in content
        assert "_priv()" in content

    def test_skip_private_flag_excludes_private(self, tmp_path: Path):
        src = tmp_path / "mypkg"
        src.mkdir()
        (src / "__init__.py").write_text("")
        (src / "mod.py").write_text(
            'def pub():\n    """Public."""\n    pass\n'
            'def _priv():\n    """Private."""\n    pass\n'
        )
        out_file = tmp_path / "out.txt"
        sys.argv = [
            "export-functions.py",
            f"--source-root={src}",
            f"--output-file={out_file}",
            "--skip-private",
        ]
        result = main()
        assert result == 1  # modified
        content = out_file.read_text(encoding="utf-8")
        assert "pub()" in content
        assert "_priv()" not in content

    def test_strict_fails_for_public_function_without_docstring(self, tmp_path: Path):
        src = tmp_path / "mypkg"
        src.mkdir()
        (src / "__init__.py").write_text("")
        (src / "mod.py").write_text("def pub():\n    pass\n")
        out_file = tmp_path / "out.txt"
        sys.argv = [
            "export-functions.py",
            f"--source-root={src}",
            f"--output-file={out_file}",
            "--strict",
        ]
        result = main()
        assert result == 1

    def test_strict_does_not_fail_for_private_function_without_docstring(
        self, tmp_path: Path
    ):
        src = tmp_path / "mypkg"
        src.mkdir()
        (src / "__init__.py").write_text("")
        (src / "mod.py").write_text(
            'def pub():\n    """Public."""\n    pass\ndef _priv():\n    pass\n'
        )
        out_file = tmp_path / "out.txt"
        sys.argv = [
            "export-functions.py",
            f"--source-root={src}",
            f"--output-file={out_file}",
            "--strict",
        ]
        result = main()
        assert result == 1  # modified (first run), not strict failure
        content = out_file.read_text(encoding="utf-8")
        assert "pub()" in content
        assert "_priv()" not in content  # no docstring, so not included

    def test_already_up_to_date(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ):
        src = tmp_path / "mypkg"
        src.mkdir()
        (src / "__init__.py").write_text("")
        (src / "mod.py").write_text('def pub():\n    """Public."""\n    pass\n')
        out_file = tmp_path / "out.txt"
        sys.argv = [
            "export-functions.py",
            f"--source-root={src}",
            f"--output-file={out_file}",
        ]
        main()  # first run to create the file
        result = main()  # second run - should be up to date
        assert result == 0
        captured = capsys.readouterr()
        assert "already up to date" in captured.out

    def test_invalid_source_root(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ):
        out_file = tmp_path / "out.txt"
        sys.argv = [
            "export-functions.py",
            "--source-root=/nonexistent/path",
            f"--output-file={out_file}",
        ]
        result = main()
        assert result == 1
        captured = capsys.readouterr()
        assert "ERROR" in captured.err
