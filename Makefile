.PHONY requirements:
requirements:
	uv pip compile "pyproject.toml" --quiet --generate-hashes --python-version 3.12 --python-platform linux --output-file .requirements/3.12-linux.txt
	uv pip compile "pyproject.toml" --quiet --generate-hashes --python-version 3.12 --python-platform macos --output-file .requirements/3.12-macos.txt 
	uv pip compile "pyproject.toml" --quiet --generate-hashes --python-version 3.12 --python-platform windows --output-file .requirements/3.12-windows.txt 