# OpenVend

Source-available modular ERP for self-hosted solo operators and micro-businesses.

OpenVend is designed around independently deployable REST-first services, a
first-class Web UI, and safe AI-agentic access through scoped MCP/CLI tools. The
product source of truth is [openvend-prd.md](openvend-prd.md).

## Phase 0 Foundation

This repository currently implements the Phase 0 foundation:

- Docker Compose trust-zone networks: `edge`, `app`, and `data`.
- Traefik edge routing for Web UI, Kratos, and APIs over the internal app network.
- Ory Kratos base browser-flow configuration.
- Authorization Adapter FastAPI service with `/health`, `/ready`, `/me`,
  `/permissions`, and `/tokens` foundations. Principal resolution fails closed
  unless development auth is explicitly enabled.
- PostgreSQL one-instance/multi-database bootstrap scripts.
- Valkey cache/queue service.
- React + TypeScript + Vite Web UI shell with sidebar, top bar, routing, theme
  toggle, and light/dark design tokens.
- OpenAPI client generation pipeline placeholder.
- CI checks for backend, frontend, Compose config, and dependency policy.

## Quick Start

Copy the environment template and start the Phase 0 stack:

```bash
cp .env.example .env
docker compose up --build
```

Default local routes:

- Web UI: http://localhost:8088
- Authorization Adapter API: http://localhost:8088/api/v1/authz
- Kratos public flows: http://localhost:8088/auth
- Traefik dashboard: http://localhost:18088

The default Compose ports bind to `127.0.0.1`. Set `OPENVEND_HTTP_BIND` and
`OPENVEND_HTTPS_BIND` deliberately when exposing the stack beyond the local
machine.

The Authorization Adapter's development principal scaffold is disabled by
default. For local-only API experiments, set:

```env
AUTHZ_DEV_AUTH_ENABLED=true
```

Do not enable this in production. `scripts/init.sh` runs
`scripts/check_runtime_config.sh` and rejects production startup when placeholder
secrets remain or development auth is enabled.

Optional TLS profile:

```bash
mkdir -p infra/traefik/certs
# Place local or production certificate material here:
#   infra/traefik/certs/openvend.crt
#   infra/traefik/certs/openvend.key
docker compose -f docker-compose.yml -f docker-compose.tls.yml up --build
```

The TLS overlay exposes HTTPS on `OPENVEND_HTTPS_PORT` (`8443` by default) and
keeps certificate files out of git.

Run local validation without Docker:

```bash
npm install
npm run check

python3 -m venv .venv
. .venv/bin/activate
pip install -e "services/authorization-adapter[dev]"
pytest services/authorization-adapter/tests
```

## Repository Layout

```text
apps/web/                         React + Vite Web UI shell
services/authorization-adapter/    FastAPI authorization foundation
infra/                             Traefik, Kratos, and Postgres config
openapi/                           Generated OpenAPI snapshots
packages/api-client/               OpenAPI client package placeholder
scripts/                           Operational and validation scripts
docs/                              Development, legal, and ADR docs
```

## License

OpenVend uses a commercial-use source-available license. See
[LICENSE.md](LICENSE.md), [NOTICE.md](NOTICE.md), and
[docs/legal/license-model.md](docs/legal/license-model.md).
