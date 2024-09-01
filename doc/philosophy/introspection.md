# Introspection when developing

Nathan McDougall, August 2024.

When developing, so many of our actions are reflexive. If you are interesting in
developing usethis, then it is very valuable to slow down, and consider thoroughly
which actions you are undertaking. Some of them might be running off-the-shelf automated
tools. Sometimes you might be setting up bespoke configuration for those tools.
Other times, you might have to do something manually.

These are all useful points to note down and can provide a lot of insight into potential
features for usethis (besides just being useful documentation).

For example, when developing usethis, here are a list of actions that I undertook (not
necessarily listed chronologically):

## Toolset decisions

- Use GitHub Actions for CI.
- Always use the hash to pin the version of a GitHub action `uses:`
- Use uv for package management.

## Repo configuration

- Created a repo on GitHub wih template .gitignore, MIT license and README.
- Created a develop branch.
- Set up sensible rulesets for branches.
- Created a template for GitHub issues that are development tasks.
- Ran `uv init --name usethis`.
- Ran `uv python pin 3.12.4`.

## Add GitHub Actions CI

- Create a GitHub workflow file for CI manually in `.github/workflows/ci.yml`.
- Use the following configuration to support GitFlow-style branch management:

```yml
name: CI
on:
    workflow_dispatch:
    push:
      branches: ['main', 'develop']
    pull_request:
```

- Add <https://github.com/hynek/setup-cached-uv>.
- Add <https://github.com/actions/checkout>.
- Set up the GitHub actions matrix to use Ubuntu, Windows and MacOS.
- Set up the GitHub actions to use different Python versions.
- Set up logic to use uv in GitHub actions.

## Local development configuration

- Cloned the repo from GitHub.
- Ran `uv sync`.
- Set up git username, email, and signing key.

## Set up tests

- Ran `uv add --dev pytest`.
- Created a tests folder.
- Added a trivial test module `test_nothing.py`.
- Add a trivial test `test_pass` to the test module.
- Add pytest, pytest-md and pytest-emoji as dev deependencies.
- Confirm pytest is working with `pytest tests` in the CLI.
- Add <https://github.com/pavelzw/pytest-action> to set up pytest in CI, using the
  correct CLI args to pytest.
