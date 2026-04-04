---
name: usethis-lesson-create
description: Create a lesson from a development difficulty, covering root cause analysis, principle generalisation, and filing as a GitHub issue
compatibility: usethis, GitHub, gh CLI
license: MIT
metadata:
  version: "1.0"
---

# Creating a Lesson

Lessons are how this project improves over time. When you encounter a difficulty, a
surprising failure, or unexpected user feedback, a lesson captures not just what happened
but _why_ — so the same mistake is not repeated by future agents or developers.

## Why root cause analysis matters

Surface-level summaries ("I forgot to run the linter") are not enough. Without
understanding the root cause, the lesson offers no actionable guidance. Root cause
analysis asks _why_ something went wrong at successive levels until a generalised
principle emerges that can guide future behaviour.

A well-formed lesson answers:

1. **What** went wrong (the observable symptom).
2. **Why** it went wrong (the root cause, not the symptom).
3. **What principle** this reveals (something actionable for the future).

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
   heuristic that applies beyond this specific situation.
4. **Fill in the lesson template** — see the template below.
5. **File as a GitHub issue** using the `usethis-github-issue-create` skill, with
   label `agent` and any other relevant labels (e.g. `bug`, `documentation`).
6. **Report the lesson** in your PR description or final progress report so reviewers
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
do Y ...".>

## Resolution

<How the problem was resolved in this instance, including any code or config changes
made. Brief — a sentence or two is enough.>

## Follow-up

<Any work that remains, such as adding an automated check, updating documentation, or
creating a related issue. Leave blank if none.>
```

## Filing the issue

Use the `usethis-github-issue-create` skill to file the completed lesson as a GitHub
issue. Choose the title to reflect the generalised principle (not just the symptom),
for example:

- **Good:** `agent: always run static checks after modifying AGENTS.md`
- **Bad:** `agent: forgot to update AGENTS.md`

Apply the `agent` label plus any other relevant labels.
