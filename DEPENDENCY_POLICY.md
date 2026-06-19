# Dependency Policy

OpenVend is source-available with commercial internal use permitted and
redistribution prohibited. Dependencies must be compatible with that model.

## Default Allowed Licenses

Prefer dependencies under:

- MIT
- BSD family licenses
- ISC
- Apache-2.0
- PostgreSQL License
- Similar permissive licenses

## Excluded by Default

Do not add default runtime dependencies under:

- AGPL
- SSPL
- RSAL
- Commons Clause
- PolyForm
- BUSL
- Copyleft or network-service terms that conflict with the product model

## Exception Process

Any exception must be:

- Optional and isolated from the default runtime.
- Documented in an ADR under `docs/adr/`.
- Reviewed before merge.
- Reflected in third-party notices.

## Operational Rules

- Do not vendor third-party source unless required and approved.
- Preserve third-party notices.
- Prefer Valkey over Redis Community Edition in the default stack.
- Run dependency and license checks before merging dependency changes.
