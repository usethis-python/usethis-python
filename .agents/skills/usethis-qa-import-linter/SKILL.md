---
name: usethis-qa-import-linter
description: Use the Import Linter software on the usethis project
compatibility: usethis, Python, import-linter
license: MIT
metadata:
  version: "1.1"
---

# Import Linter

## About

Import Linter is a static analysis tool to enforce a self-imposed architecture on imports. It allows you to define rules about how different parts of your codebase can import each other, helping to maintain a clean and organized code structure.

## Usage

```bash
uv run lint-imports
```

## Configuration File

This project uses the `.importlinter` INI file to configure Import Linter. You specify _contracts_ which need to be complied with between modules' imports. For the `usethis` project, we mainly use the `layers` contract: earlier listed "higher" layers are not allowed to import from any "lower" layers. 

### Example Structure

Where `xyz` is the name of the root package (i.e. `usethis` for this project):

```ini
[importlinter]
root_packages =
    xyz

[importlinter:contract:xyz]
name = xyz
type = layers
containers =
    xyz
layers =
    ui
    backend
    domain
exhaustive = true

[importlinter:contract:core_submodule]
name = xyz.core.submodule
type = layers
containers =
    xyz.core.submodule
layers =
    layer1
    layer2
exhaustive = true
```

## Contract Strategy

Not every module needs an associated contract for its submodules. Having contracts for every level of the module structure can lead to unnecessary maintenance overhead. Generally, it is rare to create new contracts.

## Procedure

1. Ensure the module structure complies with the Import Linter configuration.
2. Explicitly add/rename new/modified modules to their parent-level contract (to adhere to the `exhaustive` setting).
3. For major refactorings, rationalize the module structure and update the Import Linter configuration accordingly.
4. Avoid creating new contracts unless explicitly instructed.
5. Run Import Linter to verify that all contracts are satisfied.
