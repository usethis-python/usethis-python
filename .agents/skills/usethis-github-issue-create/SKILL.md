---
name: usethis-github-issue-create
description: Create GitHub issues via the gh CLI to record lessons, track follow-up work, or file bugs discovered during development
compatibility: GitHub, gh CLI, issue tracking
license: MIT
metadata:
  version: "1.0"
---

# Creating GitHub Issues via `gh` CLI

## Procedure

1. Determine the issue title and body content.
2. Assign appropriate labels.
3. Run the `gh issue create` command.
4. Report the created issue URL.

## When to create an issue

Create a GitHub issue when you:

- Discover a pre-existing bug that is out of scope for the current task.
- Identify a follow-up improvement or refactoring opportunity.
- Learn a lesson during development that should be triaged and tracked.
- Notice missing documentation, tests, or configuration that warrants separate work.

Do **not** create an issue for work you are currently addressing in your PR.

## Composing the issue

### Title

Use a concise, descriptive title. Prefix with the relevant area if applicable (e.g. `cli: ...`, `docs: ...`, `tool: ...`).

### Body

Include enough context for someone unfamiliar with the current task to understand and act on the issue. At a minimum:

- **What** the problem or opportunity is.
- **Where** in the codebase it was observed (file paths, function names).
- **Why** it matters or what impact it has.

Keep the body concise — a few sentences is usually sufficient.

### Labels

Use the `--label` flag to attach relevant labels. Check existing labels in the repository before inventing new ones. Common labels include `bug`, `enhancement`, `documentation`, and `agent`.

## Creating the issue

Use the `gh issue create` command:

```bash
gh issue create \
  --repo "<owner>/<repo>" \
  --title "<title>" \
  --body "<body>" \
  --label "<label1>,<label2>"
```

- Always specify `--repo` explicitly to avoid ambiguity.
- Use `--label` to attach one or more comma-separated labels.
- Use `--assignee @me` if you want to self-assign the issue.

## After creating the issue

- Note the issue URL returned by `gh` and include it in your PR description or progress report if it is related to the current task.
- If the issue is a direct follow-up to your current work, reference it in your commit messages or PR description (e.g. "Follow-up: #123").
