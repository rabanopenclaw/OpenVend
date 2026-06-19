#!/usr/bin/env sh
set -eu

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

set -a
. ./.env
set +a

PUBLIC_BASE_URL="${OPENVEND_PUBLIC_BASE_URL:-http://localhost:8088}"

wait_for() {
  name="$1"
  url="$2"
  attempts="${3:-60}"

  echo "Waiting for $name at $url"
  i=1
  while [ "$i" -le "$attempts" ]; do
    if curl -fsS "$url" >/dev/null; then
      echo "$name is ready"
      return 0
    fi
    i=$((i + 1))
    sleep 2
  done

  echo "$name did not become ready after $attempts attempts" >&2
  return 1
}

docker compose up --build -d
docker compose ps

wait_for "Web UI" "$PUBLIC_BASE_URL/"
wait_for "Authorization Adapter" "$PUBLIC_BASE_URL/api/v1/authz/health"
wait_for "Kratos public health" "$PUBLIC_BASE_URL/auth/health/ready"

echo "OpenVend Phase 0 stack is ready:"
echo "  Web UI: $PUBLIC_BASE_URL"
echo "  Authorization Adapter: $PUBLIC_BASE_URL/api/v1/authz"
echo "  Kratos public flows: $PUBLIC_BASE_URL/auth"
