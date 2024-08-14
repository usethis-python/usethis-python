.PHONY requirements:
requirements:
	uv pip compile "pyproject.toml" --quiet --generate-hashes --python-version 3.12 --python-platform linux --output-file .requirements/3.12-Linux.txt
	uv pip compile "pyproject.toml" --quiet --generate-hashes --python-version 3.12 --python-platform macos --output-file .requirements/3.12-macOS.txt 
	uv pip compile "pyproject.toml" --quiet --generate-hashes --python-version 3.12 --python-platform windows --output-file .requirements/3.12-Windows.txt 