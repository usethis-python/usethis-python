from pathlib import Path

import pytest

from usethis._config_file import files_manager
from usethis._integrations.project.errors import LicenseDetectionError
from usethis._integrations.project.license import (
    _get_license_from_classifiers,
    _get_license_from_file,
    _get_license_from_pyproject_field,
    get_license_id,
)
from usethis._test import change_cwd

_MIT_LICENSE_TEXT = """\
MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


class TestGetLicenseId:
    def test_from_license_file(self, tmp_path: Path):
        # Arrange
        (tmp_path / "LICENSE").write_text(_MIT_LICENSE_TEXT)

        # Act
        with change_cwd(tmp_path):
            result = get_license_id()

        # Assert
        assert result == "MIT"

    def test_from_pyproject_field(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "test"\nlicense = "Apache-2.0"\n'
        )

        # Act
        with change_cwd(tmp_path), files_manager():
            result = get_license_id()

        # Assert
        assert result == "Apache-2.0"

    def test_from_classifiers(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "test"\nclassifiers = ["License :: OSI Approved :: MIT License"]\n'
        )

        # Act
        with change_cwd(tmp_path), files_manager():
            result = get_license_id()

        # Assert
        assert result == "MIT"

    def test_raises_when_no_license(self, tmp_path: Path):
        # Act & Assert
        with change_cwd(tmp_path), pytest.raises(LicenseDetectionError):
            get_license_id()

    def test_file_takes_priority_over_pyproject(self, tmp_path: Path):
        # Arrange - both a LICENSE file and pyproject.toml license field
        (tmp_path / "LICENSE").write_text(_MIT_LICENSE_TEXT)
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "test"\nlicense = "Apache-2.0"\n'
        )

        # Act
        with change_cwd(tmp_path), files_manager():
            result = get_license_id()

        # Assert - file takes priority
        assert result == "MIT"


class TestGetLicenseFromFile:
    def test_license_file(self, tmp_path: Path):
        # Arrange
        (tmp_path / "LICENSE").write_text(_MIT_LICENSE_TEXT)

        # Act
        with change_cwd(tmp_path):
            result = _get_license_from_file()

        # Assert
        assert result == "MIT"

    def test_license_md_file(self, tmp_path: Path):
        # Arrange
        (tmp_path / "LICENSE.md").write_text(_MIT_LICENSE_TEXT)

        # Act
        with change_cwd(tmp_path):
            result = _get_license_from_file()

        # Assert
        assert result == "MIT"

    def test_licence_spelling(self, tmp_path: Path):
        # Arrange
        (tmp_path / "LICENCE").write_text(_MIT_LICENSE_TEXT)

        # Act
        with change_cwd(tmp_path):
            result = _get_license_from_file()

        # Assert
        assert result == "MIT"

    def test_no_license_file(self, tmp_path: Path):
        # Act
        with change_cwd(tmp_path):
            result = _get_license_from_file()

        # Assert
        assert result is None

    def test_unrecognized_license_content(self, tmp_path: Path):
        # Arrange - file exists but identify can't determine the license
        (tmp_path / "LICENSE").write_text("This is not a recognized license.\n")

        # Act
        with change_cwd(tmp_path):
            result = _get_license_from_file()

        # Assert
        assert result is None


class TestGetLicenseFromPyprojectField:
    def test_spdx_string(self, tmp_path: Path):
        # Arrange - PEP 639 style: license is a plain SPDX string
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "test"\nlicense = "MIT"\n'
        )

        # Act
        with change_cwd(tmp_path), files_manager():
            result = _get_license_from_pyproject_field()

        # Assert
        assert result == "MIT"

    def test_table_with_text(self, tmp_path: Path):
        # Arrange - PEP 621 style: license table with text key
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "test"\nlicense = {text = "MIT"}\n'
        )

        # Act
        with change_cwd(tmp_path), files_manager():
            result = _get_license_from_pyproject_field()

        # Assert
        assert result == "MIT"

    def test_table_with_file(self, tmp_path: Path):
        # Arrange - PEP 621 style: license table with file key
        (tmp_path / "LICENSE").write_text(_MIT_LICENSE_TEXT)
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "test"\nlicense = {file = "LICENSE"}\n'
        )

        # Act
        with change_cwd(tmp_path), files_manager():
            result = _get_license_from_pyproject_field()

        # Assert
        assert result == "MIT"

    def test_no_pyproject(self, tmp_path: Path):
        # Act
        with change_cwd(tmp_path):
            result = _get_license_from_pyproject_field()

        # Assert
        assert result is None

    def test_no_project_section(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("[tool]\n")

        # Act
        with change_cwd(tmp_path), files_manager():
            result = _get_license_from_pyproject_field()

        # Assert
        assert result is None

    def test_no_license_field(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text('[project]\nname = "test"\n')

        # Act
        with change_cwd(tmp_path), files_manager():
            result = _get_license_from_pyproject_field()

        # Assert
        assert result is None

    def test_table_with_file_not_found(self, tmp_path: Path):
        # Arrange - file key points to non-existent file
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "test"\nlicense = {file = "MISSING"}\n'
        )

        # Act
        with change_cwd(tmp_path), files_manager():
            result = _get_license_from_pyproject_field()

        # Assert
        assert result is None

    def test_table_with_empty_text(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "test"\nlicense = {text = ""}\n'
        )

        # Act
        with change_cwd(tmp_path), files_manager():
            result = _get_license_from_pyproject_field()

        # Assert
        assert result is None


class TestGetLicenseFromClassifiers:
    def test_mit_classifier(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "test"\nclassifiers = ["License :: OSI Approved :: MIT License"]\n'
        )

        # Act
        with change_cwd(tmp_path), files_manager():
            result = _get_license_from_classifiers()

        # Assert
        assert result == "MIT"

    def test_apache_classifier(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "test"\nclassifiers = ["License :: OSI Approved :: Apache Software License"]\n'
        )

        # Act
        with change_cwd(tmp_path), files_manager():
            result = _get_license_from_classifiers()

        # Assert
        assert result == "Apache-2.0"

    def test_gpl3_classifier(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "test"\nclassifiers = ["License :: OSI Approved :: GNU General Public License v3 (GPLv3)"]\n'
        )

        # Act
        with change_cwd(tmp_path), files_manager():
            result = _get_license_from_classifiers()

        # Assert
        assert result == "GPL-3.0-only"

    def test_no_classifiers(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text('[project]\nname = "test"\n')

        # Act
        with change_cwd(tmp_path), files_manager():
            result = _get_license_from_classifiers()

        # Assert
        assert result is None

    def test_no_license_classifier(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "test"\nclassifiers = ["Programming Language :: Python :: 3"]\n'
        )

        # Act
        with change_cwd(tmp_path), files_manager():
            result = _get_license_from_classifiers()

        # Assert
        assert result is None

    def test_unknown_license_classifier(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "test"\nclassifiers = ["License :: Other/Proprietary License"]\n'
        )

        # Act
        with change_cwd(tmp_path), files_manager():
            result = _get_license_from_classifiers()

        # Assert
        assert result is None

    def test_no_pyproject(self, tmp_path: Path):
        # Act
        with change_cwd(tmp_path):
            result = _get_license_from_classifiers()

        # Assert
        assert result is None
