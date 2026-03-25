---
name: usethis-cli-modify
description: Modify the usethis CLI layer (commands, options, help text) and keep documentation in sync
compatibility: usethis, Python, typer, markdown
license: MIT
metadata:
  version: "1.0"
---

# Modifying the CLI

## Procedure

1. Make your changes to the CLI layer (command functions, options, help text, or app registration).
2. Update the CLI documentation to reflect every user-facing change.
3. Run the affected interface-level tests.

## When this skill applies

Use this skill whenever you modify anything under the `_ui` package, including:

- Adding, removing, or renaming a command
- Changing a command's options, arguments, or defaults
- Changing help text or command descriptions
- Modifying how commands are registered on the app

## Update the CLI documentation

**Every user-facing CLI change requires a documentation update.** The documentation is manually written and is not auto-generated from the code, so it will not update itself.

After making CLI changes, review and update each of the following as needed:

### Command reference

The command reference page documents every command with its full description, supported options, and behavior. Update it to match any changes you made to commands, options, defaults, or descriptions.

### Command overview

The command overview page lists all commands organized by category with brief descriptions. Update it if you added, removed, renamed, or recategorized a command.

### Example usage and getting-started pages

The getting-started pages show practical CLI usage examples. If your change affects the commands or output shown in these examples, update them so the examples remain accurate and runnable.

### README

If your change adds, removes, or renames a CLI command or tool integration, update the README to reflect this.

### CONTRIBUTING.md

If your change affects the step-by-step guides in CONTRIBUTING.md (e.g. the "Adding a new tool" or "Adding a new badge" guides), update those guides to remain accurate.

## CLI architecture

### Separation of interface and core logic

Command functions in the `_ui` layer are thin wrappers. They parse CLI arguments, set up configuration and file management context, then delegate to functions in the `_core` package. Keep this separation: do not put business logic in command functions.

### Command registration pattern

Each command is defined in its own file under `_ui/interface/`. The main app object in `_ui/app.py` registers commands using `app.command()` or `app.add_typer()` for sub-apps. Shared CLI options are defined as module-level constants in `_ui/options.py`.

When adding a new command:

1. Create a new file in `_ui/interface/` following the pattern of existing commands.
2. Register it in `_ui/app.py`.
3. If the command uses shared options, import them from `_ui/options.py`. If it needs new options, add them there.
4. Create the corresponding core logic function in `_core/`.
