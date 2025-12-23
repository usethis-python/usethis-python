"""Tests for Python version utilities."""

from __future__ import annotations

import pytest

from usethis._integrations.python.version import (
    PythonVersion,
    PythonVersionParseError,
)


class TestPythonVersion:
    class TestFromString:
        def test_major_minor_only(self):
            # Act
            version = PythonVersion.from_string("3.13")

            # Assert
            assert version.major == "3"
            assert version.minor == "13"
            assert version.patch is None

        def test_major_minor_patch(self):
            # Act
            version = PythonVersion.from_string("3.10.5")

            # Assert
            assert version.major == "3"
            assert version.minor == "10"
            assert version.patch == "5"

        def test_alpha_version(self):
            # Act
            version = PythonVersion.from_string("3.14.0a3")

            # Assert
            assert version.major == "3"
            assert version.minor == "14"
            assert version.patch == "0a3"

        def test_beta_version(self):
            # Act
            version = PythonVersion.from_string("3.13.0b1")

            # Assert
            assert version.major == "3"
            assert version.minor == "13"
            assert version.patch == "0b1"

        def test_rc_version(self):
            # Act
            version = PythonVersion.from_string("3.12.0rc2")

            # Assert
            assert version.major == "3"
            assert version.minor == "12"
            assert version.patch == "0rc2"

        def test_dev_version(self):
            # Act
            version = PythonVersion.from_string("3.15.0a1+dev")

            # Assert
            assert version.major == "3"
            assert version.minor == "15"
            assert version.patch == "0a1+dev"

        def test_single_digit_minor(self):
            # Act
            version = PythonVersion.from_string("3.9.12")

            # Assert
            assert version.major == "3"
            assert version.minor == "9"
            assert version.patch == "12"

        def test_python_2(self):
            # Act
            version = PythonVersion.from_string("2.7.18")

            # Assert
            assert version.major == "2"
            assert version.minor == "7"
            assert version.patch == "18"

        def test_invalid_version_raises(self):
            # Act & Assert
            with pytest.raises(
                PythonVersionParseError, match="Could not parse Python version"
            ):
                PythonVersion.from_string("invalid")

        def test_empty_string_raises(self):
            # Act & Assert
            with pytest.raises(
                PythonVersionParseError, match="Could not parse Python version"
            ):
                PythonVersion.from_string("")

        def test_only_major_raises(self):
            # Act & Assert
            with pytest.raises(
                PythonVersionParseError, match="Could not parse Python version"
            ):
                PythonVersion.from_string("3")

    class TestToShortString:
        def test_major_minor_only(self):
            # Arrange
            version = PythonVersion(major="3", minor="13")

            # Act
            result = version.to_short_string()

            # Assert
            assert result == "3.13"

        def test_with_patch(self):
            # Arrange
            version = PythonVersion(major="3", minor="10", patch="5")

            # Act
            result = version.to_short_string()

            # Assert
            assert result == "3.10"

        def test_with_alpha_patch(self):
            # Arrange
            version = PythonVersion(major="3", minor="14", patch="0a3")

            # Act
            result = version.to_short_string()

            # Assert
            assert result == "3.14"

    class TestStr:
        def test_major_minor_only(self):
            # Arrange
            version = PythonVersion(major="3", minor="13")

            # Act
            result = str(version)

            # Assert
            assert result == "3.13"

        def test_with_patch(self):
            # Arrange
            version = PythonVersion(major="3", minor="10", patch="5")

            # Act
            result = str(version)

            # Assert
            assert result == "3.10.5"

        def test_with_alpha_patch(self):
            # Arrange
            version = PythonVersion(major="3", minor="14", patch="0a3")

            # Act
            result = str(version)

            # Assert
            assert result == "3.14.0a3"

    class TestEquality:
        def test_equal_versions(self):
            # Arrange
            v1 = PythonVersion(major="3", minor="13", patch="5")
            v2 = PythonVersion(major="3", minor="13", patch="5")

            # Act & Assert
            assert v1 == v2

        def test_equal_versions_no_patch(self):
            # Arrange
            v1 = PythonVersion(major="3", minor="13")
            v2 = PythonVersion(major="3", minor="13")

            # Act & Assert
            assert v1 == v2

        def test_unequal_minor(self):
            # Arrange
            v1 = PythonVersion(major="3", minor="13")
            v2 = PythonVersion(major="3", minor="12")

            # Act & Assert
            assert v1 != v2

        def test_unequal_patch(self):
            # Arrange
            v1 = PythonVersion(major="3", minor="13", patch="5")
            v2 = PythonVersion(major="3", minor="13", patch="4")

            # Act & Assert
            assert v1 != v2

    class TestImmutability:
        def test_frozen_dataclass(self):
            # Arrange
            version = PythonVersion(major="3", minor="13")

            # Act & Assert
            with pytest.raises(AttributeError):
                version.major = "4"  # type: ignore[misc]
