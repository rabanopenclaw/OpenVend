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
- GPL
- LGPL
- MPL
- EPL
- CDDL
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

## Approved Scanner Exceptions

- `certifi` under MPL-2.0 is allowed for development/audit tooling as a CA
  certificate bundle. It must not be used as a precedent for adding MPL
  business-logic dependencies to the default runtime.

## Operational Rules

- Do not vendor third-party source unless required and approved.
- Preserve third-party notices.
- Prefer Valkey over Redis Community Edition in the default stack.
- Run dependency and license checks before merging dependency changes.
