# Claude Code Instructions

Read `AGENTS.md` first. `openvend-prd.md` is the product source of truth.

Work one feature slice at a time. Do not code until you have written a short
implementation plan that names affected services, APIs, databases, UI surfaces,
auth rules, audit events, tests, and license impact.

Preserve these invariants:

- REST-only inter-service communication.
- Database-per-service ownership.
- Ory Kratos for human identity.
- Authorization Adapter for roles, scopes, service tokens, API keys, and agent
  tokens.
- API-to-UI parity for public operations.
- Audit logging for write actions.
- Source-available license notices and third-party attribution.
