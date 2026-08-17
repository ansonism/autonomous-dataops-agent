# AGENTS.md — Autonomous DataOps Agent

## Repository purpose

Coordinate specialized agents to reduce data-platform MTTR while preserving human control, change safety, evidence trails, idempotency, and rollback capability.

## Instructions for coding agents

1. Read `SKILL.md` before making architectural changes.
2. Preserve provider neutrality. Domain logic must not import a vendor SDK directly.
3. Put external-system interactions behind typed adapters in `tools/` or `providers/`.
4. Maintain deterministic unit tests using `MockProvider`.
5. Prefer structured Pydantic models over unvalidated dictionaries at boundaries.
6. Do not add autonomous production mutation without an explicit approval gate, allow-list and audit event.
7. Add tests and eval cases for every new failure mode.
8. Update `docs/architecture.md` and add an ADR for material design decisions.
9. Never commit credentials, tokens, private keys, connection strings or real customer data.
10. Keep CLI behavior backwards-compatible unless an ADR explains the change.

## Definition of done

A change is done only when code, tests, docs, sample configuration and eval coverage are updated together.
