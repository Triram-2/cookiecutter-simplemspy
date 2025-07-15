# {{cookiecutter.project_name}}

{{cookiecutter.project_description}}

## Development quick start

Install dependencies using [uv](https://github.com/astral-sh/uv):

```bash
uv sync
```

Run linters and tests:

```bash
nox -s ci-3.12 ci-3.13
```

Start the application for development:

```bash
uv run src/{{cookiecutter.python_package_name}}/main.py
```
