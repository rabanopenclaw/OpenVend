# Contacts API Parity Registry

Issue: #17

This registry classifies the Contacts Service public endpoints introduced by the
Phase 1 Contacts API slice. First-class human UI workflows are tracked by #19.

| Endpoint / capability | UI parity state | UI location | Required role/scope | Confirmation level | Audit requirement | Screenshot evidence |
|---|---|---|---|---|---|---|
| `GET /health` | `hidden-system` | System health | Public health endpoint | None | No | Not required |
| `GET /ready` | `hidden-system` | System readiness | Public health endpoint | None | No | Not required |
| `GET /contact-types` | `first-class-ui` | Contacts create/edit form (#19) | `contacts:read` | None | No | Pending #19 |
| `GET /contacts` | `first-class-ui` | Contacts list (#19) | `contacts:read` | None | No | Pending #19 |
| `POST /contacts` | `first-class-ui` | Contacts create dialog (#19) | `contacts:write` | None | Structured audit log | Pending #19 |
| `GET /contacts/{id}` | `first-class-ui` | Contact detail (#19) | `contacts:read` | None | No | Pending #19 |
| `PATCH /contacts/{id}` | `first-class-ui` | Contact edit dialog (#19) | `contacts:write` | None | Structured audit log | Pending #19 |
| `DELETE /contacts/{id}` | `first-class-ui` | Contact detail danger zone (#19) | `contacts:write` | Danger confirmation | Structured audit log | Pending #19 |
| Address CRUD | `first-class-ui` | Contact detail addresses panel (#19) | `contacts:read`, `contacts:write` | Delete confirmation | Structured audit log for writes | Pending #19 |
| Communication channel CRUD | `first-class-ui` | Contact detail communication panel (#19) | `contacts:read`, `contacts:write` | Delete confirmation | Structured audit log for writes | Pending #19 |
| Tag CRUD and assignment | `first-class-ui` | Contacts list/detail tag controls (#19) | `contacts:read`, `contacts:write` | Delete confirmation | Structured audit log for writes | Pending #19 |
| Activity CRUD | `first-class-ui` | Contact activity timeline (#19) | `contacts:read`, `contacts:write` | Delete confirmation | Structured audit log for writes | Pending #19 |
| Organization membership CRUD | `first-class-ui` | Contact organization membership panel (#19) | `contacts:read`, `contacts:write` | Delete confirmation | Structured audit log for writes | Pending #19 |

## Notes

- The API currently accepts forwarded scopes through `X-OpenVend-Scopes`. This
  is a Phase 1 service boundary contract until the Authorization Adapter provides
  durable token validation middleware.
- Write audit events are emitted as structured service logs. Durable audit-log
  storage remains a later audit slice.
