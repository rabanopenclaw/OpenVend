# ADR 0001: Phase 0 Stack

## Status

Accepted for Phase 0.

## Context

The PRD selects a low-footprint self-hosted stack for solo operators and
micro-businesses.

## Decision

Phase 0 uses:

- Python 3.12 compatible FastAPI services.
- SQLAlchemy/Alembic-ready service layout.
- PostgreSQL with one database per module.
- Valkey for cache and lightweight queues.
- Traefik for edge routing.
- Ory Kratos for identity flows.
- React, TypeScript, Vite, and Tailwind CSS for the Web UI.
- OpenAPI-generated clients as the API contract bridge.
- Traefik file-provider routes targeting Compose service DNS names on the
  internal `app` network.

The file provider is used for Phase 0 because it keeps routing verifiable on
hosts where Traefik's Docker provider cannot negotiate a compatible Docker API
version and avoids mounting the Docker socket into the public edge container.

## Consequences

Framework replacement, auth-provider replacement, database topology changes, or
license-impacting dependency changes require a new ADR before implementation.
