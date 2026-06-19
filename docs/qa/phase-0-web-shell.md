# Phase 0 Web Shell Screenshot Evidence

Date: 2026-06-19

Source: Phase 0 Web UI shell from `apps/web`, built with `npm run build`.

## Evidence

| View | Screenshot |
|---|---|
| Desktop light mode | `docs/qa/screenshots/phase-0/web-shell-light.png` |
| Desktop dark mode | `docs/qa/screenshots/phase-0/web-shell-dark.png` |

## Notes

- Light and dark desktop screenshots were captured from the local Compose stack at `http://127.0.0.1:8088/`.
- A tablet-width capture exposed a horizontal page scrollbar in the responsive navigation.
- The responsive shell CSS was updated so tablet navigation is constrained to the viewport and scrolls inside the navigation row.
- A refreshed tablet screenshot could not be captured in this environment after the fix because Docker rebuild access and headless Chrome sandbox access were blocked.
