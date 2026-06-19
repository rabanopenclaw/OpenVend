#!/usr/bin/env sh
set -eu

if [ -x ".venv/bin/python" ]; then
  exec .venv/bin/python scripts/export_openapi.py
fi

exec python3 scripts/export_openapi.py
