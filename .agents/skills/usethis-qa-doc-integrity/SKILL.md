---
name: usethis-qa-doc-integrity
description: Audit CLI documentation for completeness and sync with source code — checks that every command option visible in the code appears in the reference documentation
compatibility: usethis, CLI, markdown
license: MIT
metadata:
  version: "1.0"
---

# CLI Documentation Integrity

The CLI reference documentation is written by hand and is not auto-generated from code. It can drift out of sync when CLI options are added, changed, or removed without a corresponding documentation update.

## Procedure

1. For each command or subcommand of interest, read the command function signature in the `_ui/interface/` source.
2. Compare every option parameter in the signature against the corresponding entry in `docs/cli/reference.md`.
3. For shared options (defined once in `_ui/options.py` and reused across commands), confirm that each command that accepts the option has it documented — not just the first command it was introduced for.
4. Check that every subcommand is listed in the reference's subcommand inventory for its parent command.
5. Fix any gaps found.

## What to look for

### Missing options

An option present in the function signature but absent from the reference. This is the most common gap — it happens when a shared option is added to new commands without updating all their doc entries, or when a new option is added to one command in a group but only documented for another.

### Missing subcommands

A subcommand (e.g. `usethis show license`) that exists in the code but is not listed in the parent command's subcommand inventory in the reference.

### Stale entries

An option documented in the reference that no longer exists in the code. These should be removed.

## Scope of a full audit

A full audit covers every command exposed by the CLI app. Check each command function for:

- All option parameters
- All argument parameters
- Any command-specific sub-options (e.g. options that only apply to one subcommand within a group)

Shared options that apply uniformly to all commands in a group (e.g. `--offline`, `--quiet`) may be documented once at the group level rather than repeated for each subcommand — as long as this is consistent and the group-level entry is present.

Options that are not uniform across a group (e.g. an option added to only some subcommands) must appear explicitly in each subcommand's entry or in a clearly labelled "additional options" note.

## Relation to other skills

Use `usethis-cli-modify` for guidance on keeping documentation in sync as part of a CLI change workflow. This skill is for standalone audits and for verifying completeness after the fact.
