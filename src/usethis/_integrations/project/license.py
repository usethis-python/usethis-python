"""License detection for the project."""

from __future__ import annotations

import os

from identify.identify import license_id

from usethis._file.pyproject_toml.errors import PyprojectTOMLError
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._integrations.project.errors import LicenseDetectionError

_CANDIDATE_LICENSE_FILENAMES = [
    "LICENSE",
    "LICENSE.md",
    "LICENSE.txt",
    "LICENSE.rst",
    "LICENCE",
    "LICENCE.md",
    "LICENCE.txt",
    "LICENCE.rst",
    "COPYING",
    "COPYING.md",
    "COPYING.txt",
]

_CLASSIFIER_TO_SPDX: dict[str, str] = {
    "License :: OSI Approved :: Academic Free License (AFL)": "AFL-3.0",
    "License :: OSI Approved :: Apache Software License": "Apache-2.0",
    "License :: OSI Approved :: Artistic License": "Artistic-2.0",
    "License :: OSI Approved :: BSD License": "BSD-3-Clause",
    "License :: OSI Approved :: Boost Software License 1.0 (BSL-1.0)": "BSL-1.0",
    "License :: OSI Approved :: CEA CNRS Inria Logiciel Libre License, version 2.1 (CeCILL-2.1)": "CECILL-2.1",
    "License :: OSI Approved :: Eclipse Public License 1.0 (EPL-1.0)": "EPL-1.0",
    "License :: OSI Approved :: Eclipse Public License 2.0 (EPL-2.0)": "EPL-2.0",
    "License :: OSI Approved :: European Union Public Licence 1.1 (EUPL 1.1)": "EUPL-1.1",
    "License :: OSI Approved :: European Union Public Licence 1.2 (EUPL 1.2)": "EUPL-1.2",
    "License :: OSI Approved :: GNU Affero General Public License v3": "AGPL-3.0-only",
    "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)": "AGPL-3.0-or-later",
    "License :: OSI Approved :: GNU Free Documentation License (FDL)": "GFDL-1.3-only",
    "License :: OSI Approved :: GNU General Public License (GPL)": "GPL-3.0-only",
    "License :: OSI Approved :: GNU General Public License v2 (GPLv2)": "GPL-2.0-only",
    "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)": "GPL-2.0-or-later",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)": "GPL-3.0-only",
    "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)": "GPL-3.0-or-later",
    "License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)": "LGPL-2.0-only",
    "License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)": "LGPL-2.0-or-later",
    "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)": "LGPL-3.0-only",
    "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)": "LGPL-3.0-or-later",
    "License :: OSI Approved :: ISC License (ISCL)": "ISC",
    "License :: OSI Approved :: MIT License": "MIT",
    "License :: OSI Approved :: MIT No Attribution License (MIT-0)": "MIT-0",
    "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)": "MPL-2.0",
    "License :: OSI Approved :: MulanPSL v2": "MulanPSL-2.0",
    "License :: OSI Approved :: The Unlicense (Unlicense)": "Unlicense",
    "License :: OSI Approved :: Universal Permissive License (UPL)": "UPL-1.0",
    "License :: OSI Approved :: zlib/libpng License": "Zlib",
}


def get_license_id() -> str:
    """Get the SPDX license identifier for the current project.

    Uses heuristics in the following order:
    1. Scan common license files at the project root using the `identify` package.
    2. Read the `project.license` field from `pyproject.toml`.
    3. Check `project.classifiers` in `pyproject.toml` for license classifiers.

    Raises:
        LicenseDetectionError: If the license cannot be determined.
    """
    result = _get_license_from_file()
    if result is not None:
        return result

    result = _get_license_from_pyproject_field()
    if result is not None:
        return result

    result = _get_license_from_classifiers()
    if result is not None:
        return result

    msg = "Could not detect a project license. Add a 'LICENSE' file, or set 'project.license' in 'pyproject.toml'."
    raise LicenseDetectionError(msg)


def _get_license_from_file() -> str | None:
    """Try to detect the license from common license files at the project root."""
    for filename in _CANDIDATE_LICENSE_FILENAMES:
        if os.path.isfile(filename):
            spdx_id = license_id(filename)
            if spdx_id is not None:
                return spdx_id
    return None


def _get_license_from_pyproject_field() -> str | None:
    """Try to detect the license from pyproject.toml `project.license` field."""
    try:
        pyproject = PyprojectTOMLManager().get().value
    except PyprojectTOMLError:
        return None

    project = pyproject.get("project")
    if not isinstance(project, dict):
        return None

    license_value = project.get("license")
    if license_value is None:
        return None

    # PEP 639: license is a string SPDX expression
    if isinstance(license_value, str):
        return license_value

    # PEP 621: license is a table with 'text' or 'file' key
    if not isinstance(license_value, dict):
        return None

    return _resolve_license_table(license_value)


def _resolve_license_table(license_value: dict[str, object]) -> str | None:
    """Resolve a PEP 621 license table to an SPDX identifier."""
    # If it has a 'text' key, the text itself might be an SPDX identifier
    text = license_value.get("text")
    if isinstance(text, str) and text.strip():
        return text.strip()

    # If it has a 'file' key, try to scan that file
    file_path = license_value.get("file")
    if isinstance(file_path, str) and os.path.isfile(file_path):
        return license_id(file_path)

    return None


def _get_license_from_classifiers() -> str | None:
    """Try to detect the license from pyproject.toml `project.classifiers`."""
    try:
        pyproject = PyprojectTOMLManager().get().value
    except PyprojectTOMLError:
        return None

    project = pyproject.get("project")
    if not isinstance(project, dict):
        return None

    classifiers = project.get("classifiers")
    if not isinstance(classifiers, list):
        return None

    for classifier in classifiers:
        if not isinstance(classifier, str):
            continue
        if not classifier.startswith("License :: "):
            continue
        spdx_id = _CLASSIFIER_TO_SPDX.get(classifier)
        if spdx_id is not None:
            return spdx_id

    return None
