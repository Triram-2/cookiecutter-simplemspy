# Cookiecutter Simple MSPy

This repository provides a cookiecutter template for creating a small high-performance Python microservice.

## Quick start

1. Install [cookiecutter](https://cookiecutter.readthedocs.io/):
   ```bash
   pip install --user cookiecutter
   ```
2. Generate a project from this template:
   ```bash
   cookiecutter https://github.com/Triram-2/cookiecutter-simplemspy
   ```
3. Move into the created directory and install dependencies using [uv](https://github.com/astral-sh/uv):
   ```bash
   uv sync
   ```
4. Run tests and linters:
   ```bash
   nox -s ci-3.12 ci-3.13
   ```
5. Build documentation:
   ```bash
   nox -s docs
   ```
6. Start the development server:
   ```bash
   uv run src/{{cookiecutter.python_package_name}}/main.py
   ```

The generated service exposes two endpoints:
- `GET /health` – health information
- `POST /tasks` – accepts a payload and stores a task in Redis Streams returning `202 Accepted`

Additional helper scripts are located in the `scripts/` folder to automate systemd service creation.

## Configuration

Environment variables are loaded from `.env` using Pydantic settings. The most
important ones are:

- `APP_HOST` / `APP_PORT` – host and port for Uvicorn
- `APP_RELOAD` – enable auto reloading
- `APP_ENV` – environment name (`dev`, `prod`, `test`)
- `REDIS_URL` – Redis connection string
- `STATSD_HOST` / `STATSD_PORT` – StatsD exporter address
- `JAEGER_HOST` / `JAEGER_PORT` – Jaeger collector endpoint
- `LOKI_ENDPOINT` – Loki push endpoint for logs

The template ships with a `.env.example` file containing defaults.

## Running with Docker Compose

Launch the service together with Redis, StatsD, Jaeger and Loki:

```bash
docker-compose up -d
```

Containers use `restart: unless-stopped` so they will automatically start on
host reboot. The compose file relies on the environment variables listed above,
so adjust them if necessary.

## Metrics and tracing

Metrics are sent via a lightweight StatsD client defined in
`src/utils/metrics.py`. When OpenTelemetry is available, traces are exported to
Jaeger via `src/utils/tracing.py`. If `LOKI_ENDPOINT` is set, structured logs are
pushed to Loki.

## Graceful shutdown

`src/api/main.py` registers a shutdown handler that closes Redis connections,
resets the StatsD client and clears collected spans before the application
exits. This ensures a clean termination.
