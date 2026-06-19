# OpenVend Agent Instructions

These instructions apply to the entire repository. The product source of truth is
`openvend-prd.md`; read the relevant PRD sections before planning or editing.

## Product Summary

OpenVend is a source-available, modular ERP-style platform for solo operators
and micro-businesses. The v1 target is a single-host Docker Compose deployment
for contacts, inventory, quotes/orders, reporting, exports, and safe AI-agentic
access.

The product has three first-class access paths:

- Human Web UI.
- Versioned REST APIs.
- AI-agentic access through MCP and CLI.

The license model is commercial-use source-available, not OSI open source:
commercial internal use is allowed, redistribution/resale/public hosted SaaS
offering is prohibited without separate permission, and attribution/credits and
third-party notices must remain intact.

## Non-Negotiable Architecture Rules

- Use REST APIs for all module-to-module communication.
- Do not connect one module directly to another module's database.
- The Web UI must call the same public REST APIs as external clients and agents.
- Keep database ownership per service. V1 uses one PostgreSQL instance with one
  database per module.
- Keep Docker trust zones separated: `edge`, `app`, and `data`.
- Databases must never be reachable from `edge`.
- Services must be stateless outside their own datastore.
- Use Ory Kratos for human identity, browser flows, recovery, verification, and
  session lifecycle.
- Keep ERP authorization in the Authorization Adapter: roles, scopes, service
  tokens, API keys, agent tokens, and policy decisions.
- Every write action must be authorized server-side and audit-logged.
- AI/MCP/CLI access must use scoped tokens, rate limits, audit logging, and
  confirmation flows for destructive or high-impact actions.

## Selected Stack

Do not replace these choices without an Architecture Decision Record under
`docs/adr/` and explicit maintainer approval:

- Backend services: Python 3.12 + FastAPI.
- Data layer: SQLAlchemy 2.x + Alembic.
- Database: PostgreSQL, one instance with one database per module.
- Cache/queue: Valkey.
- Edge/gateway: Traefik.
- Auth provider: Ory Kratos.
- Authorization: small ERP Authorization Adapter.
- Web UI: React + TypeScript + Vite.
- UI system: Tailwind CSS, shadcn/ui, Radix primitives, Lucide icons.
- Client state/tables/forms: TanStack Query, TanStack Table, React Hook Form,
  Zod.
- Charts: Recharts.
- Reporting/export: pandas, openpyxl, ReportLab.
- AI-agentic access: official Python MCP SDK plus a thin CLI using the same REST
  clients.

## Module Boundaries

Each business module must be independently testable and deployable:

- Own Docker Compose service.
- Own REST API under `/api/v1/<module>`.
- Own OpenAPI spec.
- Own database/schema and Alembic migrations.
- Own health and readiness endpoints.
- Own tests and smoke-test path.
- Own UI parity entries for public endpoints.

Core modules from the PRD:

- Contacts.
- Inventory.
- Quotes and Orders.
- Reporting.
- Flexible Export.
- Web UI / Admin Console.
- AI-Agent Gateway.
- Authorization Adapter.

Cross-module references should use opaque IDs plus denormalized display snapshots
where useful. Do not introduce shared business tables.

## API and UI Parity

Every public REST endpoint must have a UI parity classification:

- `first-class-ui`: normal business workflow with validation, permissions, empty
  states, and error handling.
- `admin-ui`: available through an admin/developer screen or API action
  explorer.
- `hidden-system`: internal health/readiness/service endpoint.
- `deprecated`: compatibility endpoint with migration notes.

No business write endpoint may ship without a first-class UI workflow or an
admin UI action. OpenAPI definitions are the source of truth for generated UI
clients and API docs.

Each parity entry must include endpoint/capability, UI location, role/scope,
confirmation level, audit requirement, and screenshot evidence when applicable.

## Plan-First Workflow

Every implementation task starts with a short plan before code changes. Keep the
work to one feature slice unless the maintainer explicitly approves a broader
scope.

Before editing, identify:

- Business goal.
- Affected module(s).
- Public or internal APIs involved.
- Database entities and migrations.
- UI screens, dialogs, or admin/API explorer entries.
- Authorization roles/scopes.
- Audit logging requirements.
- External dependencies and license impact.
- Acceptance criteria.
- Test plan.
- Rollback or recovery notes for risky changes.

After implementation, report:

- Changed files.
- Migration notes, if any.
- Tests and checks run.
- Screenshots for UI changes.
- Known limitations.
- Follow-up tasks.

## Definition of Done

A feature is not done until all relevant items are handled:

- API implementation is complete.
- OpenAPI spec is updated.
- UI access exists for all relevant public API actions.
- Generated clients are updated where applicable.
- Database migrations are included and reversible where practical.
- Authorization checks are enforced server-side.
- Write actions are audit-logged.
- Tests pass for affected services.
- Loading, empty, error, and success UI states are covered where relevant.
- Light and dark mode screenshots are captured for UI changes.
- Documentation is updated.
- Dependency/license scan remains acceptable.
- Known limitations are documented.

## UI Requirements

The Web UI is a first-class product surface, not a privileged admin shortcut.

- Build dashboard-first workflows with left navigation, compact KPI cards, chart
  panels, and an assistant/action panel where appropriate.
- Support light and dark mode from Phase 0.
- Centralize semantic design tokens: background, surface, elevated surface,
  border, muted text, accent, success, warning, and danger.
- Use theme-aware charts.
- Keep screens keyboard-accessible.
- Include clear loading, empty, error, and success states.
- Destructive actions require confirmation UX and audit events.
- Provide screenshot evidence for desktop light mode, desktop dark mode, and
  narrow/tablet layout when the layout changes materially.

## Security, Auth, and Audit

- Ory Kratos handles human identity and browser auth flows.
- The Authorization Adapter handles roles, scopes, service tokens, API keys, and
  agent tokens.
- Public API endpoints must explicitly declare auth strategy: Kratos session,
  API token, service token, agent token, or public health endpoint.
- Enforce RBAC at the API layer, not only in the UI.
- Never commit secrets, tokens, `.env` files, private keys, or local credentials.
- Use `.env` or Docker secrets for configuration.
- Add structured audit events for all write operations and privacy-relevant
  exports.
- Agent-initiated writes must be visible in the audit log.
- Destructive/high-impact agent actions must support human confirmation queues.

## Dependency and License Policy

Default dependency posture:

- Prefer MIT, BSD, ISC, Apache-2.0, PostgreSQL License, or similarly permissive
  licenses.
- Preserve third-party notices and attribution.
- Maintain `THIRD_PARTY_NOTICES.md` once dependency scanning is introduced.
- Do not vendor third-party source unless necessary.
- Do not add AGPL, SSPL, RSAL, Commons Clause, PolyForm, BUSL, or other
  restrictive/copyleft/source-available runtime dependencies by default.
- Any exception must be optional, isolated, documented, and approved before
  merge.

Use Valkey, not Redis Community Edition, in the default stack.

## Testing and Validation

For each affected service, prefer focused validation first and broader checks
when shared contracts change.

Expected checks as the repo grows:

- Python tests for backend services.
- Alembic migration checks.
- OpenAPI generation/validation.
- Frontend type checks and tests.
- UI screenshot checks for visible changes.
- Docker Compose smoke tests for service readiness.
- Dependency and license scans.
- API parity registry enforcement.

Do not claim a check passed unless you ran it. If a check cannot run, state why.

## GitHub Issues and Pull Requests

Implementation issues should use the PRD's plan-first structure:

```md
## Goal
## Scope
## Out of Scope
## Affected Services
## API Changes
## Database Changes
## UI Changes
## Auth / Permission Rules
## Audit Logging
## Dependency / License Impact
## Acceptance Criteria
## Test Plan
## Rollback / Recovery Notes
```

Pull requests should include:

```md
## Summary
## Feature Slice
## API / OpenAPI Changes
## Database Migrations
## UI Parity Registry Updates
## Auth / Permission Checks
## Audit Events
## Tests Run
## Screenshots
- Light mode:
- Dark mode:
- Narrow viewport, if relevant:
## Dependency / License Changes
## Known Limitations
```

## Stop and Ask

Stop and ask for maintainer approval before:

- Changing product scope, license terms, or redistribution rules.
- Replacing Ory Kratos or bypassing the Authorization Adapter.
- Merging service databases or adding shared business tables.
- Weakening auth, authorization, audit logging, or network segmentation.
- Adding incompatible or unclear-license dependencies.
- Replacing major frontend/backend frameworks.
- Introducing public SaaS or multi-tenant assumptions to v1.
- Performing broad refactors inside a feature implementation task.
- Removing attribution, credits, license text, or third-party notices.
- Implementing destructive actions without confirmation UX and audit events.
- Committing generated outputs, vendored code, or build artifacts whose purpose
  is not clear.
