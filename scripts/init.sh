#!/usr/bin/env sh
set -eu

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

docker compose up --build -d
docker compose ps

echo "OpenVend Phase 0 stack requested. Check readiness with:"
echo "  curl http://localhost/api/v1/authz/health"
