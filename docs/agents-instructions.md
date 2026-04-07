# Generally Important Instructions

- ALWAYS check the [Function Reference](../AGENTS.md#function-reference) section in AGENTS.md before implementing any utility logic — mature, tested functions already exist for common operations such as reading dependencies, detecting tools, and printing console output.
- ALWAYS use possibly relevant agent skills when they are available. Eagerly use skills, if in doubt, assume a skill is relevant.
- ALWAYS dogfood and user-test CLI changes. After implementing or modifying any CLI command, use the `usethis-cli-dogfood` skill to run the command against this repo and the `usethis-cli-user-test` skill to verify the happy path in a fresh project. Both are mandatory — never skip them, even for seemingly simple changes. Use the `usethis-cli-modify` skill for guidance on the full CLI change workflow.
- ALWAYS use the `usethis-skills-modify` skill when modifying any agent skill (`SKILL.md` file). Do not edit skill files without it — it enforces version bumping, scope checking, and content quality guidelines. Similarly, ALWAYS use `usethis-skills-create` when creating a new skill.
- ALWAYS use `find-skills` to research new skill capabilities if there are difficult tasks, tasks in an unfamiliar domain, if you believe there is a lack of clarity or direction around precisely how to proceed, or if you get stuck or find something surprisingly challenging. When using this skill, please be sure to use the `usethis-skills-external-install` skill when deciding to install a new external skill.
- ALWAYS consider the `usethis-python-test-full-coverage` to be relevant: if your task involves
  writing or modifying code, always use this skill to write tests and verify full coverage
  before finishing. Aim for 100% coverage on new or changed code.
- ALWAYS consider the `usethis-qa-static-checks` to be relevant: if you think your task is complete, always run this skill to check for any issues before finishing. You must fix **all** static check failures, including pre-existing ones unrelated to your changes. This applies to ALL changes, including documentation-only changes and skill file edits — static checks catch sync issues, formatting problems, and other regressions that affect every file type. CI enforces checks on the entire codebase, so unfixed failures will block your PR. **After fixing any failure or making any further change, re-run ALL static checks again from scratch — even if you ran them moments ago.** It is expected and normal to run this skill repeatedly in a loop until every check passes cleanly.
- ALWAYS mention which skills you've used after completing any task, in PR descriptions, and comments.
- ALWAYS reference the relevant issue ID in PR descriptions using a closing keyword, e.g. `Resolves #123`. This ensures traceability between PRs and the issues they address.

## Lessons

When you are working on a problem, you are almost always going to encounter a difficulty. This is great — it's an opportunity for learning. ALWAYS make a note explicitly of what lessons you are drawing as you complete a task or when receiving user feedback. After finishing work on a task, report back all your lessons. Use the `usethis-lesson-create` skill to perform root cause analysis, generalise the principle at play, and file each lesson as a GitHub issue so it can be triaged and tracked.
