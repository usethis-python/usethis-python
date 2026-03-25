---
name: usethis-python-ruff
description: Guidelines for complying with Ruff linter rules instead of suppressing them
compatibility: usethis, Python, Ruff
license: MIT
metadata:
  version: "1.0"
---

# Ruff Rule Compliance

When Ruff flags a violation, the default response should be to **fix the code**, not suppress the warning. Only suppress a rule as a last resort.

## Procedure

1. When a Ruff violation appears, first try to auto-fix it by running:

   ```bash
   uv run ruff check --fix --unsafe-fixes
   ```

2. If auto-fix doesn't resolve it, manually update the code to comply with the rule.
3. Only if the rule genuinely cannot be satisfied should you add a `# noqa` comment — and if you do, you **must** include an explanatory comment justifying why.
4. Before adding any `# noqa`, check whether the rule code is in the never-suppress list below. If it is, you must find a way to comply.

## Rules that must never be suppressed

The following rule codes must **never** be suppressed with `# noqa`. Always fix the code to comply:

- **`TC`** (flake8-type-checking rules, e.g. `TC001`, `TC002`, `TC003`): Move imports into or out of `TYPE_CHECKING` blocks as the rule requires. The `--fix --unsafe-fixes` command can often resolve these automatically.

## When `# noqa` is acceptable

A `# noqa` comment is acceptable only when **all** of the following are true:

- Auto-fix (`--fix --unsafe-fixes`) does not resolve the violation.
- Manually rewriting the code to comply is not feasible or would make the code significantly worse.
- The rule code is **not** in the never-suppress list above.

When you do add a `# noqa`, always place a comment on the same line or adjacent line explaining **why** the suppression is necessary. A bare `# noqa: XXXX` without justification is not acceptable.
