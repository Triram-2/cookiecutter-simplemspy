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
   uv run src/main.py
   ```

The generated service exposes two endpoints:
- `GET /health` – health information
- `POST /tasks` – accepts a payload and stores a task in Redis Streams returning `202 Accepted`

Additional helper scripts are located in the `scripts/` folder to automate systemd service creation.
