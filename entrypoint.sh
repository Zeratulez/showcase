#!/bin/sh

# Stops script when error occurs
set -e

alembic upgrade head

exec fastapi run ./app/main.py --port 8000