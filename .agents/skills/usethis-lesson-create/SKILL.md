---
name: usethis-lesson-create
description: Create a lesson from a development difficulty, covering root cause analysis, principle generalisation, and filing as a GitHub issue
compatibility: usethis, GitHub, gh CLI
license: MIT
metadata:
  version: "1.2"
---

# Creating a Lesson

Lessons are how this project improves over time. When you encounter a difficulty, a
surprising failure, or unexpected user feedback, a lesson captures not just what happened
but _why_ — and proposes a concrete action to prevent the same mistake from recurring.

A lesson is **not** a record of what was done to fix a one-off problem. It is a proposal
for a lasting improvement: an update to an agent skill, a new or improved linting/prek
hook, or a code refactor that structurally prevents the class of issue.

## Why root cause analysis matters

Surface-level summaries ("I forgot to run the linter") are not enough. Without
understanding the root cause, the lesson offers no actionable guidance. Root cause
analysis asks _why_ something went wrong at successive levels until a generalised
principle emerges that can guide future behaviour.

A well-formed lesson answers:

1. **What** went wrong (the observable symptom).
2. **Why** it went wrong (the root cause, not the symptom).
3. **What principle** this reveals (something actionable for the future).
4. **What concrete action** would prevent recurrence (a skill update, a hook, or a
   refactor — not just "be more careful next time").

## Self-containment and abstraction

Lessons must stand alone. A lesson is read in future sessions with no access to prior
context, stored memories, or conversation history. Therefore:

- **Never reference memories.** Do not write phrases like "as noted in a previous
  session", "per the stored memory about X", or "see the earlier lesson on Y". A reader
  with no history must be able to understand and apply the lesson without looking anything
  up.
- **Never name specific code objects unless they are the subject.** If the principle is
  about a pattern, name the pattern — not the exact function, class, or file where you
  first encountered it. Specific names become stale and narrow the lesson's applicability.
- **State principles at the right level of abstraction.** A good principle applies to an
  entire class of situations. Ask yourself: would this guidance still be useful if the
  specific file or function that triggered it were renamed or removed? If not, generalise
  further.

### Examples of abstraction

| Too specific                                                            | Better                                                                                          |
| ----------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Always call `clear_functools_caches()` after adding `@functools.cache`. | Whenever a caching decorator is added, ensure the cache is cleared in tests.                    |
| `validate_or_raise` accepts `err=`, not `error_cls`.                    | Validation helpers often have specific argument conventions — check the signature before use.   |
| Update `AGENTS.md` when adding a skill to `.agents/skills/`.            | Keep all registry files in sync whenever a new entry is added to a tracked directory.           |
| Put new helpers in `src/mypackage/_utils/helpers.py`.                   | Place new helpers near their primary caller, following the project's module layout conventions. |

## When to create a lesson

Create a lesson whenever you:

- Encounter a problem that took more than one attempt to solve.
- Receive corrective user feedback or a review rejection.
- Discover a project convention that was not obvious from the code.
- Make an error that could easily be repeated without explicit guidance.

Do **not** create a lesson for trivial fixes (typos, missing imports) where the root
cause is self-evident and offers no transferable principle.

## Procedure

1. **Identify the difficulty** — note the symptom: what failed, was rejected, or
   surprised you.
2. **Perform root cause analysis** — ask "why?" iteratively to move from the
   symptom to an underlying cause. See the section below.
3. **Generalise the principle** — restate the root cause as a transferable rule or
   heuristic that applies beyond this specific situation. Write it so it remains useful
   even if the exact code, file, or function name changes. Avoid naming specific
   implementation details unless the principle is truly about that specific thing.
   See the "Self-containment and abstraction" section above for guidance.
4. **Propose a concrete action** — every lesson must recommend at least one specific
   improvement. Choose from these categories (in order of preference):
   - **Skill update** — add or revise guidance in an existing agent skill so future
     agents avoid the mistake. This is the most common and preferred action.
   - **Automated check** — propose a new or improved linting rule, prek hook, or CI
     check that catches the mistake automatically.
   - **Code refactor** — suggest a structural change to the code that makes the mistake
     impossible or much harder to make.

   Do **not** simply record what was done to fix the immediate instance. The action must
   prevent the _class_ of problem, not just the single occurrence.

5. **Fill in the lesson template** — see the template below.
6. **File as a GitHub issue** using the `usethis-github-issue-create` skill, with
   label `agent` and any other relevant labels (e.g. `bug`, `documentation`).
7. **Report the lesson** in your PR description or final progress report so reviewers
   are aware.

## Root cause analysis

Work iteratively through the "5 Whys" technique:

1. Start with the symptom.
2. Ask "Why did this happen?" and write the answer.
3. Ask "Why did _that_ happen?" about the new answer.
4. Repeat until you reach a root cause that is structural or principled, not just
   situational.

Stop when one more "why" would leave the domain of the project (e.g. "because Python
allows it" is not actionable).

### Example

| Level      | Statement                                                                             |
| ---------- | ------------------------------------------------------------------------------------- |
| Symptom    | The CI pipeline failed because a hook was not updated.                                |
| Why 1      | The hook list in AGENTS.md was not kept in sync with the skills directory.            |
| Why 2      | There was no automated check enforcing that sync.                                     |
| Root cause | Sync between two authoritative sources was manual with no enforcement.                |
| Principle  | Any two artefacts that must stay in sync need an automated check; manual sync drifts. |
| Action     | Add a prek hook that verifies the skills table in AGENTS.md matches the directory.    |

## Lesson template

Use this template when composing the GitHub issue body.

```markdown
## What happened

<One or two sentences describing the observable symptom — what failed, was rejected,
or produced an unexpected result.>

## Root cause

<The underlying reason this happened, reached by asking "why?" iteratively. State the
cause, not the symptom.>

## Generalised principle

<A transferable rule or heuristic — written so it applies beyond this specific
situation. Phrase it as actionable guidance: "Always ...", "Never ...", "When X,
do Y ...". Avoid naming specific functions, classes, or files unless the principle is
truly about that specific thing. Do not reference memories or prior sessions.>

## Recommended action

<One or more concrete improvements to prevent this class of problem from recurring.
Each action should fall into one of these categories:

- **Skill update:** which skill to update and what guidance to add or revise.
- **Automated check:** a new or improved linting rule, prek hook, or CI check to add.
- **Code refactor:** a structural change that makes the mistake impossible or harder.

Do not record what was done to fix the immediate instance — focus on what should change
to prevent recurrence. If the recommended action has already been completed as part of
the current session, say so, but still describe the action clearly so the issue can be
verified and closed.>
```

## Filing the issue

Use the `usethis-github-issue-create` skill to file the completed lesson as a GitHub
issue. Choose the title to reflect the generalised principle (not just the symptom),
for example:

- **Good:** `agent: always run static checks after modifying AGENTS.md`
- **Bad:** `agent: forgot to update AGENTS.md`

Apply the `agent` label plus any other relevant labels.
