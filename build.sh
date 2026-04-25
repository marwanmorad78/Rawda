#!/usr/bin/env bash
set -o errexit

uv sync --frozen --no-dev
uv run python src/manage.py collectstatic --noinput
