# usethis

Automate Python project setup and development tasks that are otherwise performed manually.

usethis is a command-line interface to automate the configuration of popular Python tools, workflows, and frameworks. You can use it to declaratively add, remove, and configure tools in an existing project, as well as set up a new project from scratch. It won't break your existing configuration, and ensures all tools work together smoothly.

usethis gives detailed messages about what it is doing (and what you need to do next).

- Output beginning with `✔` represents a task which usethis has automated.
- Output beginning with `☐` represents a task which you need to perform manually.
- Output beginning with `ℹ` gives hints and tips.

Inspired by an [**R** package of the same name](https://usethis.r-lib.org/index.html), this package brings a similar experience to the Python ecosystem as a CLI tool.

usethis is great for fresh projects using [uv](https://docs.astral.sh/uv), but also supports updating existing projects. However, this should be considered experimental. If you encounter problems or have feedback, please [open an issue](https://github.com/usethis-python/usethis-python/issues/new?template=idea.md).

## Highlights

- 🧰 First-class support for state-of-the-practice tooling: uv, Ruff, pytest, pre-commit, and many more.
- 🤖 Automatically add and remove tools: declare, install, and configure in one step.
- 🧠 Powerful knowledge of how different tools interact and sensible defaults.
- 🔄 Update existing configuration files automatically.
- 📢 Fully declarative project configuration.
- ⚡ Get started on a new Python project or a new workflow in seconds.
