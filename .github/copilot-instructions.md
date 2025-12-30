# Copilot Instructions

## Project Overview

**usethis** is a CLI tool that automates Python project setup and development tasks. It declaratively adds, removes, and configures popular Python tools (uv, Ruff, pytest, pre-commit, MkDocs, etc.) in existing projects without breaking configuration. The tool provides detailed ✔/☐/ℹ messages about what it automated and what users need to do next.

**Tech Stack:** Python 3.10-3.14, uv package manager, Typer CLI framework, Rich for terminal output, pydantic for validation, tomlkit/ruamel-yaml for config files.

**Repository Size:** 100-500 Python files across src/ and tests/ directories. Project follows trunk-based development on `main` branch.

## Critical Build & Environment Requirements

### Environment Setup (REQUIRED FIRST STEP)
1. **ALWAYS run `uv sync` first** after cloning or before any development work. This installs all dependencies including dev, test, and doc groups.
2. Python version: Use 3.10.18 (specified in `.python-version`). The CI tests 3.10-3.14, but development uses oldest supported version.
3. uv version: Minimum 0.8.18 required (documented in README and `pyproject.toml`). Check with `uv --version`.

### Running Commands
**Critical:** ALWAYS prefix Python commands with `uv run` to use the project environment:
- ✅ `uv run pytest`
- ✅ `uv run ruff check`
- ✅ `uv run prek install`
- ❌ Never use bare `pytest`, `ruff`, etc.

**Common Warning:** You may see warnings like "Failed to uninstall package at .venv\Lib\site-packages\usethis-*.dist-info due to missing RECORD file." This is normal and doesn't affect functionality.

**Interacting with git**: Try to avoid interacting with git directly without user instruction. Don't ever modify `.gitignore` or other git config files without explicit user consent.

## Testing

### Running Tests
```bash
# Run all tests (takes ~5-30 seconds depending on scope)
uv run pytest

# Run specific test file
uv run pytest tests/test_help.py -v

# Run with coverage (required before commits)
uv run pytest --cov --cov-report=xml

# Run specific tests by name pattern
uv run pytest -k "test_help" -v
```

**Test Requirements:**
- All tests must pass before committing
- Coverage target: 95% (configured in codecov.yaml)
- Test structure mirrors source: `src/x/y/z.py` → `tests/x/y/test_z.py`
- Use arrange-act-assert structure with comments separating sections
- Only one contiguous block of assertions in assert section
- Tests organized into classes: `TestMyClass` containing `TestMyMethod` for nested method tests
- **No side-effects**: Tests must not modify, create, or delete files in the repository directory
  - Always use pytest's `tmp_path` fixture for file operations
  - Always use `usethis._test.change_cwd` context manager when testing code that operates on the current working directory
  - Example: `with change_cwd(tmp_path): do_something()`
  - If a test modifies repo files, it's a sign the CWD is not properly set with `change_cwd`

## Validation Pipeline (Pre-Commit Checks)

### Install Git Hooks
```bash
uv run prek install
```

### Pre-Commit Checks (runs on every commit)
The following checks run automatically via prek (pre-commit framework). All must pass:

1. **sync-with-uv** - Syncs pre-commit hooks with uv.lock
2. **uv-lock** - Ensures uv.lock is up to date (`uv lock --offline`)
3. **uv-sync** - Syncs dependencies (`uv sync --no-active --offline --locked`)
4. **uv-export** - Exports requirements.txt (`uv export --frozen --offline -o=requirements.txt`)
5. **uv-export-docs** - Exports docs requirements
6. **Standard checks** - Large files, case conflicts, merge conflicts, YAML validity, debug statements, test naming
7. **pyproject-fmt** - Formats pyproject.toml
8. **Ruff** - Linter and formatter (`uv run ruff check --fix` and `uv run ruff format`)
9. **deptry** - Checks for missing/unused dependencies (`uv run deptry src`)
10. **codespell** - Spell checker
11. **import-linter** - Enforces architecture constraints (`uv run lint-imports`)
12. **ty** - Type checker (`uv run ty`)

**To run all checks manually:**
```bash
uv run prek run --all-files
```

**Individual validation commands:**
```bash
uv run ruff check --fix           # Linter with autofixes
uv run ruff format                # Formatter
uv run deptry src                 # Dependency checker
uv run codespell                  # Spell checker
uv run lint-imports               # Architecture constraints
uv run ty                         # Type checker
```

## Architecture & Project Structure

### Source Code Layout
```
src/usethis/
  __main__.py           # CLI entry point (calls _ui.app)
  _ui/                  # User interface layer
    app.py              # Main Typer app
    interface/          # Command implementations (init, tool, lint, format, etc.)
    options/            # CLI options/arguments
  _toolset/             # High-level tool operations
  _core/                # Core business logic (badge, tool, author, ci, etc.)
  _tool/                # Tool abstraction layer
    impl/               # Specific tool implementations (ruff, pytest, mkdocs, etc.)
    base.py             # Base tool classes
    config.py, rule.py, pre_commit.py
  _config_file.py       # Config file handling
  _integrations/        # External system integrations
    file/               # File format handlers (toml, yaml, ini, pyproject_toml, setup_cfg)
    backend/            # Build backend integrations
    ci/                 # CI system integrations (github, bitbucket)
    environ/, mkdocs/, project/, python/, pytest/, etc.
  _io.py, _subprocess.py, _console.py  # Low-level utilities
  _config.py            # Global state and constants
  _types/, errors.py    # Type definitions and error classes
  _pipeweld/            # Functional programming utilities
  _deps.py, _init.py    # Dependency and init operations
```

### Architecture Enforcement
**CRITICAL:** Import Linter enforces strict layering. The architecture contract in `pyproject.toml` defines allowed dependencies between modules. Running `uv run lint-imports` validates this. Key rules:
- `_ui` depends on `_toolset` → `_core` → `_tool` → `_config_file` → `_integrations` → low-level utilities
- `_pipeweld` is completely independent
- See `[[tool.importlinter.contracts]]` in pyproject.toml for full layer definitions

### Global Configuration State (`usethis_config`)

**CRITICAL:** The `usethis._config.usethis_config` object manages global application state. This is used to avoid pass-through variables that would otherwise need to be threaded through many layers of function calls.

**When to use global state:**
- ✅ **DO** use `usethis_config` for settings that affect application behavior across many different commands
- ✅ **DO** use it for application-wide concerns: output verbosity (`quiet`, `alert_only`, `instruct_only`), network access (`offline`), dependency installation (`frozen`), build backend (`backend`), etc.
- ❌ **DO NOT** add new global state for command-specific behavior that only affects a single CLI command
- ❌ **DO NOT** use it for passing data between functions (use function parameters instead)

**Requirements for adding new global state:**
1. There must be a very good reason - the default should be to use function parameters
2. The state must be useful across the whole application, not just one or two commands
3. The purpose must be to control application behavior (e.g., how output is displayed, whether network is allowed), not the specific business logic of a command
4. Document the new state clearly in the `UsethisConfig` docstring

**How it works:**
- `usethis_config.set()` is a context manager that temporarily overrides settings
- CLI commands use it to apply command-line flags: `with usethis_config.set(offline=offline, quiet=quiet):`
- Internal functions access current config: `if usethis_config.quiet: return`
- Settings are automatically restored when the context manager exits

See CONTRIBUTING.md Architecture section for detailed documentation and examples.

### Configuration Files
- `pyproject.toml` - Main project config, dependencies, tool configurations (Ruff, pytest, coverage, import-linter)
- `uv.lock` - Lock file (committed to repo)
- `.python-version` - Python version (3.10.18)
- `.pre-commit-config.yaml` - Pre-commit hook definitions
- `mkdocs.yml` - Documentation configuration
- `codecov.yaml` - Coverage requirements (95% target)
- `.readthedocs.yaml` - ReadTheDocs build config

## CI/CD Pipeline

### GitHub Actions Workflows (in `.github/workflows/`)

**ci.yml** - Main CI pipeline (runs on push to main, PRs, and daily cron):
- Matrix testing: Python 3.10-3.14 × (ubuntu/macos/windows)
- Also tests min dependencies (3.10 + uv 0.8.18) and max dependencies (3.14 + latest)
- Runs prek checks, pytest with coverage
- CodSpeed benchmarking (Python 3.13)
- Codecov upload (Python 3.14)
- All tests must pass

**release.yml** - PyPI release (triggered on tags matching `v*`):
- Runs on ubuntu-latest with Python 3.12
- Builds with `uv build`
- Publishes with `uv publish --trusted-publishing always`

**codeql.yml** - Security scanning (CodeQL for Python and GitHub Actions)

**zizmor.yml** - GitHub Actions workflow security linting

### Important CI Behaviors
- Tests skip on changes to `docs/**`, `**/*.md`, `mkdocs.yml`
- Git user config is set in CI: `git config --global user.name placeholder`
- Concurrency: Cancels in-progress runs on same ref

## Development Workflow

### Adding New Features

1. **Check for GitHub Issue** - Ensure an issue exists before starting work (required by CONTRIBUTING.md)

2. **Setup environment:**
   ```bash
   uv sync
   uv run prek install
   ```

3. **Make changes** following architecture layers

4. **Add dependencies** (if needed):
   ```bash
   uv add <package>                  # Runtime dependency
   uv add --dev <package>            # Dev dependency
   uv add --group test <package>     # Test dependency
   uv add --group doc <package>      # Doc dependency
   ```

5. **Write tests** in `tests/` mirroring source structure

6. **Run validation:**
   ```bash
   uv run pytest                     # Tests
   uv run pytest --cov               # Coverage
   uv run prek run --all-files       # All pre-commit checks
   ```

7. **Build documentation** (optional):
   ```bash
   uv run mkdocs serve               # Serve docs locally at http://127.0.0.1:8000
   uv run mkdocs build               # Build static site to site/
   ```

### Adding support for a New Badge
Follow the guide in CONTRIBUTING.md:
1. Add `get_<badge_name>_badge` function in `src/usethis/_core/badge.py`
2. Declare interface in `src/usethis/_ui/interface/badge.py`
3. Add test in `tests/usethis/_ui/interface/test_interface_badge.py`
4. Update badge order in `get_badge_order` function

### Code Conventions

**Python Style:**
- Line length: 88 characters (Ruff default)
- Type hints: Use strict literals `Literal["a", "b"]` over broad `str`
- Use `isinstance()` not `hasattr()` for type checking
- Modern generics: `list[int]` not `typing.List[int]`
- Keyword-only args: Use `*` separator for most arguments except 1-2 most important
- Print statements: Use `usethis._console.plain_print()` (never bare `print()`) to respect `--quiet` flag
- Use `pathlib.Path` for all filesystem operations (not `os.path`)

**Docstrings:**
- Google style format
- NO type annotations in docstrings (already in function signature)
- Example: `text:` not `text (str):`

**Linting:**
- Avoid suppressions unless absolutely necessary
- Format: `# ruff: noqa: RULE1, RULE2` (not `# ruff noqa:`)

## Trust These Instructions

These instructions have been validated by running actual commands and inspecting the full codebase. Only search for additional information if:
- These instructions are incomplete for your specific task
- You find information that conflicts with these instructions
- You need file contents not summarized here

## Quick Reference Card

| Task | Command |
|------|---------|
| First-time setup | `uv sync` |
| Install git hooks | `uv run prek install` |
| Run tests | `uv run pytest` |
| Run tests with coverage | `uv run pytest --cov` |
| Run all checks | `uv run prek run --all-files` |
| Format code | `uv run ruff format` |
| Lint code | `uv run ruff check --fix` |
| Check types | `uv run ty` |
| Check dependencies | `uv run deptry src` |
| Check architecture | `uv run lint-imports` |
| Serve docs | `uv run mkdocs serve` |
| Build package | `uv build` |
| Add dependency | `uv add <pkg>` or `uv add --dev <pkg>` |
