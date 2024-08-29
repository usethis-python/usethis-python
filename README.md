# usethis

Automate Python package and project setup tasks that are otherwise performed manually.

## Development

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

### Terminology

A usethis function will run a _workflow_. Some workflows add and configure _tools_,
others add and configure _source code_. Some allow you to _browse_ somewhere.

### Keeping Config Sections Synchronized

Tools are not configured independently from one another. For example, if we are using
pytest, we might want to enable the PTD rules in ruff, whereas if we are not using
pytest, it really doesn't make sense to do this. Another example would be shared config,
e.g. if two tools both need to know that the source code is in the `src` folder. One
last example is a tool that cannot be used at all without another, e.g. setuptools_scm
requires that we have setuptools in the first place.

These three examples illustrate three scenarios of tool dependence:

- Partial Dependency,
- Shared Dependency, and
- Full Dependency.

Each usethis function is potentially the dependent for another, and itself might have
dependents. Both directions need to be considered when the function is designed and
tested. To aid with this, usethis functions record dependencies using a registration
system using a decorator, which allows us to form a graph structure for the dependency
relationships.

Generally, information for tool configuration should be in `pyproject.toml` in the
appropriate section. In rare cases, it might be necessary to store information in a
`[tool.usethis]` section, although this is not yet clear.

To maintain synchronization between tools, the registration allows us to track through
the chain of dependencies to ensure that all relevant re-configurations take place, if
any.
