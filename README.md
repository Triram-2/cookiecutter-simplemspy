# Cookiecutter Simple MSPy

Cookiecutter template for building extremely fast Python microservices. The generated project uses **Starlette** with **Uvicorn** and processes tasks asynchronously through Redis Streams. Monitoring is available via StatsD, Jaeger and Grafana Loki.

## Features

- Sub-millisecond REST API returning `202 Accepted`
- Fire-and-forget task queue based on Redis Streams
- Docker Compose stack for local development
- Nox sessions for linting, tests, docs and builds

## Quick start

1. Install cookiecutter:
   ```bash
   pip install cookiecutter
   ```
2. Generate a project from this template:
   ```bash
   cookiecutter https://github.com/Triram-2/cookiecutter-simplemspy
   ```
3. Change into the created directory:
   ```bash
   cd <project_slug>
   ```
4. Install dependencies with [uv](https://github.com/astral-sh/uv):
   ```bash
   uv sync
   ```
5. Start required services and run tests:
   ```bash
   docker-compose up -d
   uv run pytest
   ```
6. Launch the development server:
   ```bash
   uv run src/<python_package_name>/main.py
   ```

List available Nox commands with:
```bash
nox -l
```

## Configuration

Copy `.env.example` to `.env` and adjust values. Important options include:

- `APP_HOST` / `APP_PORT` – address for Uvicorn
- `REDIS_URL` – Redis connection string
- `STATSD_HOST` / `STATSD_PORT` – StatsD exporter
- `JAEGER_ENDPOINT` – Jaeger collector endpoint
- `LOKI_ENDPOINT` – Loki push endpoint

Refer to `.env.example` for all variables.

## Endpoints

- `GET /health` – service status
- `POST /tasks` – enqueue a task and immediately respond with `202 Accepted`

## Documentation

Build HTML docs with:
```bash
nox -s docs
```


