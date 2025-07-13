#!/bin/bash
set -euo pipefail

# Prepare local development environment.
# Requires uv (https://github.com/astral-sh/uv) to be installed.

if ! command -v uv >/dev/null 2>&1; then
    echo "uv is required. Install it with: pipx install uv" >&2
    exit 1
fi

uv venv .venv
uv sync

echo "Environment ready. Activate with 'source .venv/bin/activate'."
