# Philosophy

usethis targets the Python ecosystem in a particular way. It's not trying to be a package manager: that's well covered by `uv`. It's also not trying to provide absolutely all the functionality a developer might want, e.g. CI, editor, and LLM configuration. Instead, usethis focuses on the Python-specific aspects of Python developer tooling and project configuration.

## Why not CI Configuration?

Until v0.19.0, usethis provided a `usethis ci` command, but this was deprecated for removal. It's worth giving some of the rationale for why, since it helps to clarify the philosophy of usethis.

- There are many different CI providers, external services, and configurations that people might want to use. That variety is in tension with the usethis philosophy of generally providing a single, opinionated way to do things. There's often an element of setting up broader infrastructure, API keys, etc. and altogether this makes it very difficult to automate effectively.

- CI configuration has important security implications to consider. It's not something that is necessary sensible to try and automate compared to Python developer tooling and project configuration.

- Directing dev tooling through tools for managing hooks like [prek](https://prek.j178.dev/) and [pre-commit](https://pre-commit.com/) limits the value in also configuring CI, since the CI configuration is generally just invoking these tools.
