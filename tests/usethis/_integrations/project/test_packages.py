from pathlib import Path

from usethis._integrations.project.packages import get_importable_packages
from usethis._test import change_cwd


class TestGetImportablePackages:
    def test_dir_in_src(self, tmp_path: Path):
        """Test that a directory in src is detected as importable."""
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "foo").mkdir()
        (tmp_path / "src" / "foo" / "__init__.py").touch()
        (tmp_path / "src" / "foo" / "bar.py").touch()

        with change_cwd(tmp_path):
            assert get_importable_packages() == {"foo"}

    def test_dir_in_root(self, tmp_path: Path):
        """Test that a directory in the root is detected as importable."""
        (tmp_path / "foo").mkdir()
        (tmp_path / "foo" / "__init__.py").touch()
        (tmp_path / "foo" / "bar.py").touch()

        with change_cwd(tmp_path):
            assert get_importable_packages() == {"foo"}

    def test_nothing(self, tmp_path: Path):
        """Test that no directories are detected as importable."""
        (tmp_path / "src").mkdir()
        (tmp_path / "foo").mkdir()

        with change_cwd(tmp_path):
            assert get_importable_packages() == set()

    def test_test_dir_ignored(self, tmp_path: Path):
        """Test that a test directory is ignored."""
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "tests").mkdir()
        (tmp_path / "src" / "tests" / "__init__.py").touch()
        (tmp_path / "src" / "tests" / "test_foo.py").touch()

        with change_cwd(tmp_path):
            assert get_importable_packages() == set()

    def test_namespace_package(self, tmp_path: Path):
        """Test that a namespace package is detected as importable."""
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "spam").mkdir()
        (tmp_path / "src" / "spam" / "subpackage").mkdir()
        (tmp_path / "src" / "spam" / "subpackage" / "__init__.py").touch()

        with change_cwd(tmp_path):
            assert get_importable_packages() == {"spam.subpackage"}

    def test_multiple_namespace_packages(self, tmp_path: Path):
        """Test that multiple namespace packages are detected as importable."""
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "foo").mkdir()
        (tmp_path / "src" / "foo" / "__init__.py").touch()
        (tmp_path / "src" / "bar").mkdir()
        (tmp_path / "src" / "bar" / "__init__.py").touch()

        with change_cwd(tmp_path):
            assert get_importable_packages() == {"foo", "bar"}

    def test_flat_layout_excludes_root_py_files(self, tmp_path: Path):
        """Test that root-level .py files are excluded in a flat layout.

        In a flat layout (no src/ directory), standalone .py files like
        setup.py or conftest.py should not be detected as importable packages.
        Only directories with __init__.py should be included.
        """
        (tmp_path / "foo").mkdir()
        (tmp_path / "foo" / "__init__.py").touch()
        (tmp_path / "foo" / "bar.py").touch()
        # Root-level .py files that should be excluded
        (tmp_path / "setup.py").touch()
        (tmp_path / "conftest.py").touch()

        with change_cwd(tmp_path):
            # Should only include "foo" package, not "setup" or "conftest" modules
            assert get_importable_packages() == {"foo"}

    def test_src_layout_excludes_root_py_files(self, tmp_path: Path):
        """Test that root-level .py files are excluded in a src/ layout.

        In a src/ layout, standalone .py files in src/ like __init__.py
        (without a package directory) should not be detected as importable packages.
        """
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "foo").mkdir()
        (tmp_path / "src" / "foo" / "__init__.py").touch()
        (tmp_path / "src" / "foo" / "bar.py").touch()
        # Root-level .py files in src/ that should be excluded
        (tmp_path / "src" / "conftest.py").touch()
        (tmp_path / "src" / "helper.py").touch()

        with change_cwd(tmp_path):
            # Should only include "foo" package, not "conftest" or "helper" modules
            assert get_importable_packages() == {"foo"}
