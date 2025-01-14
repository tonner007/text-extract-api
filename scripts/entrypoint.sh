#!/bin/bash

PYPROJECT_HASH_FILE=".pyproject.hash"
CURRENT_HASH=$(sha256sum pyproject.toml | awk '{ print $1 }')

if [ ! -d ".venv" ] || [ ! -f "$PYPROJECT_HASH_FILE" ] || [ "$(cat $PYPROJECT_HASH_FILE)" != "$CURRENT_HASH" ]; then
  echo "Dependencies have changed or .venv is missing. Reinstalling..."
  python -m venv .venv
  source .venv/bin/activate
  pip install --upgrade pip setuptools wheel
  pip install .
  echo "$CURRENT_HASH" > "$PYPROJECT_HASH_FILE"
else
  echo "Virtual environment is up to date."
fi

source .venv/bin/activate

if [ "$APP_MODE" = "celery" ]; then
  echo "Starting Celery worker..."
  exec celery -A text_extract_api.celery_app worker --loglevel=info --pool=solo
else
  echo "Starting FastAPI app..."
  if [ "$APP_ENV" = "production" ]; then
    exec uvicorn text_extract_api.main:app --host 0.0.0.0 --port 8000
  else
    exec uvicorn text_extract_api.main:app --host 0.0.0.0 --port 8000 --reload
  fi
fi
