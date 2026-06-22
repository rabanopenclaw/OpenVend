#!/usr/bin/env sh
set -eu

env_file="${1:-.env}"

if [ -f "$env_file" ]; then
  case "$env_file" in
    */*) env_source="$env_file" ;;
    *) env_source="./$env_file" ;;
  esac
  set -a
  . "$env_source"
  set +a
fi

is_truthy() {
  case "$(printf '%s' "${1:-}" | tr '[:upper:]' '[:lower:]')" in
    1 | true | yes | on) return 0 ;;
    *) return 1 ;;
  esac
}

has_placeholder() {
  value="$1"
  case "$value" in
    "" | replace-with-* | openvend-dev-password) return 0 ;;
    *) return 1 ;;
  esac
}

failures=0

if [ "${OPENVEND_ENV:-development}" = "production" ]; then
  for variable_name in \
    POSTGRES_PASSWORD \
    KRATOS_COOKIE_SECRET \
    KRATOS_CIPHER_SECRET \
    AUTHZ_SERVICE_TOKEN_SECRET
  do
    eval "value=\${$variable_name:-}"
    if has_placeholder "$value"; then
      echo "Invalid production config: $variable_name must be set to a non-placeholder value." >&2
      failures=$((failures + 1))
    fi
  done

  if is_truthy "${AUTHZ_DEV_AUTH_ENABLED:-false}"; then
    echo "Invalid production config: AUTHZ_DEV_AUTH_ENABLED must be false." >&2
    failures=$((failures + 1))
  fi
fi

if [ "$failures" -gt 0 ]; then
  exit 1
fi

echo "Runtime configuration check passed."
