# 📚 Similar Projects

Not sure if usethis is the exact fit for your project?

The closest match to usethis is [PyScaffold](https://github.com/pyscaffold/pyscaffold/). It provides a Command Line Interface to automate the creation of a project from a sensible templated structure.

You could also consider your own hard-coded template. Templating tools such as [Cookiecutter](https://github.com/cookiecutter/cookiecutter) and [Copier](https://github.com/copier-org/copier) allow you to create static templates with fixed configuration you can use across multiple projects. However, it's not always obvious which template you should use, and many do not use state-of-practice tooling such as `pyproject.toml`. Also, sometimes a template can overwhelm you with too many unfamiliar tools.

You could consider [this template](https://github.com/pawamoy/copier-uv) or [this one](https://github.com/jlevy/simple-modern-uv), which work with Copier, or [this template](https://github.com/johnthagen/python-blueprint) which works with Cookiecutter.

You can still use usethis as a part of a templates using [hooks](https://cookiecutter.readthedocs.io/en/latest/advanced/hooks.html#using-pre-post-generate-hooks-0-7-0) for Cookiecutter and [tasks](https://copier.readthedocs.io/en/stable/configuring/#tasks) for Copier.

If you're using Cookiecutter, then you can update to a latest version of a template using a tool like [cruft](https://github.com/cruft/cruft). Copier has inbuilt support for template updating. Another template-style option which provides updating is [jaraco/skeleton](https://blog.jaraco.com/skeleton/), which is a specific, git-based template rather than a general templating system.

If you're not interested in templating automations, then [configurator](https://github.com/jamesbraza/configurator) provides a list of useful tooling and configuration to consider for your Python projects.
