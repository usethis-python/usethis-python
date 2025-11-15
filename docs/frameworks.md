# Using Frameworks with usethis

If you are adopting a specific framework like Django, FastAPI, or Dagster, the following approaches may be useful to you. They require that you have `uv` installed. Please [open an issue](https://github.com/usethis-python/usethis-python/issues) is you use a framework which is not listed below.

## Django

[Django](https://docs.djangoproject.com/en/5.2/ref/django-admin/#startproject) has a built-in initialization command. It is recommended that you run the following sequence of commands to initialize a new Django project with usethis.

You should replace `myproject` with the name of your project, and run these commands from a new, empty directory (usually sharing your project name and set as the git repository root).

```bash
uvx --from django django-admin startproject myproject .
uv init --bare
uv add django
usethis init
```

You will be able to run the server with `uv run manage.py runserver`.

## FastAPI

[FastAPI](https://fastapi.tiangolo.com/) has an official CLI tool for initializing new projects called [`fastapi-new`](https://github.com/fastapi/fastapi-new) which you can use alongside usethis.

You should replace `myproject` with the name of your project, and run these commands from a new, empty directory (usually sharing your project name and set as the git repository root).

```bash
uvx fastapi-new myproject .
uvx usethis init
```

You will then be able to run the server with `uv run fastapi dev`.

## Dagster

[Dagster](https://docs.dagster.io/) has an official CLI tool for initializing new projects called [`create-dagster`](https://docs.dagster.io/api/clis/create-dagster) which you can use alongside usethis.

You should run these commands from a new, empty directory (usually sharing your project name and set as the git repository root).

```bash
uvx create-dagster project .
# At this point you will be prompted whether you want to use uv; answer 'y'.
uvx usethis init
```
