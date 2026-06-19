# AI-Assisted Development Workflow

OpenVend is expected to be built with human review and AI coding agents. The
human maintainer owns product scope, architecture, security posture, licensing,
and final merge decisions.

## Required Flow

1. Read `AGENTS.md`, `openvend-prd.md`, and any relevant issue.
2. Produce a short implementation plan.
3. Implement one feature slice.
4. Update API, UI, auth, audit, docs, and tests together when the slice touches
   them.
5. Run focused checks and report exact commands.
6. Provide screenshots for visible UI changes.

## Stop Conditions

Stop and ask before changing license terms, replacing Kratos, bypassing the
Authorization Adapter, merging service databases, weakening audit logging,
introducing incompatible dependencies, or broadening the feature slice.
