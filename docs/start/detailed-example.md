# 💡 Detailed Example

The output from usethis is chatty. If you know what you're doing, you can suppress it with the `--quiet` option, but usually it's worth paying close attention. For example, when adding the Ruff linting and formatting tool with the command `usethis tool ruff`, this is the output:

```console
$ uvx usethis tool ruff
✔ Adding dependency 'ruff' to the 'dev' group in 'pyproject.toml'.
✔ Adding Ruff config to 'pyproject.toml'.
✔ Selecting Ruff rules 'A', 'C4', 'E4', 'E7', 'E9', 'F', 'FLY', 'FURB', 'I', 'PLE', 'PLR', 'RUF', 'SIM'4, 'UP' in 'pyproject.toml'.
✔ Ignoring Ruff rules 'PLR2004', 'SIM108' in 'pyproject.toml'.
☐ Run 'uv run ruff check --fix' to run the Ruff linter with autofixes.
☐ Run 'uv run ruff format' to run the Ruff formatter.
```

Let's run through what each line of the output means:

1. `✔ Adding dependency 'ruff' to the 'dev' group in 'pyproject.toml'.`  
   This line indicates that the `ruff` package has been added as a development dependency in the `pyproject.toml` file. This means that `ruff` has been installed automatically via `uv`, but also that it is recorded in the project's dependency list for others when they start working on the project (e.g. with `uv sync`).
2. `✔ Adding Ruff config to 'pyproject.toml'.`
    This line indicates that a configuration section for Ruff has been added to the `pyproject.toml` file. This section contains settings that control how Ruff behaves when it is run. The settings adopted by usethis are "context aware" - based on the structure of your project, other tools you are using, etc., and so they are more likely to be appropriate for your project than the default settings.
3. `✔ Selecting Ruff rules 'A', 'C4', 'E4', 'E7', 'E9', 'F', 'FLY', 'FURB', 'I', 'PLE', 'PLR', 'RUF', 'SIM', 'UP' in 'pyproject.toml'.`
    This line indicates that a set of recommended Ruff rule sets has been selected and added to the `pyproject.toml` configuration. These rules determine what kinds of issues Ruff will check for in your code. The selected rules are based on best practices and are intended to help you maintain high code quality. Most of them have auto-fixes available. You can learn more about the specific rules in the [Ruff documentation](https://docs.astral.sh/ruff/rules).
4. `✔ Ignoring Ruff rules 'PLR2004', 'SIM108' in 'pyproject.toml'.`  
    This line indicates that certain Ruff rules have been explicitly ignored in the configuration. These rules were deemed less useful or potentially problematic for most projects, so usethis has chosen to disable them by default. You can always modify this list later if you find that you want to enable or disable additional rules.
5. `☐ Run 'uv run ruff check --fix' to run the Ruff linter with autofixes.`  
    This line is an instruction for you to run the Ruff linter on your codebase. It helps teach you how to use the tool which has just been installed and configured. You're ready to go and explore!
6. `☐ Run 'uv run ruff format' to run the Ruff formatter.`
    Ruff is also a code formatter. Similar to the previous line, this is an instruction for you to run the Ruff formatter on your codebase. This will help ensure that your code adheres to consistent formatting standards.

The key idea is that lines beginning with a check mark (✔) indicate actions that have been successfully completed by usethis, while lines beginning with an empty box (☐) are instructions for you to follow up on.
