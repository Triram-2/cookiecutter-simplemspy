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

### Running with Docker Compose

Copy the provided example environment file and start the stack:

```bash
cp .env.example .env
nox -s compose_rebuild
```

Start the application for development:

```bash
uv run src/{{cookiecutter.python_package_name}}/main.py
```
