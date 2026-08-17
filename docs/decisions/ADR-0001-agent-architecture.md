# ADR-0001: Use provider-neutral, workflow-oriented agent architecture

**Status:** Accepted

## Context

Coordinate specialized agents to reduce data-platform MTTR while preserving human control, change safety, evidence trails, idempotency, and rollback capability.

The project must support multiple model vendors and deterministic local testing without coupling domain logic to a specific SDK or orchestration framework.

## Decision

Use:
- a small internal workflow/orchestrator abstraction,
- typed Pydantic state models,
- a `BaseLLMProvider` interface,
- typed tool adapters,
- explicit evidence/risk models,
- mock/fake implementations for CI and local demos.

Avoid selecting a heavy external agent framework until domain requirements prove it is necessary.

## Consequences

Positive:
- vendor neutrality,
- easy testing,
- transparent workflow semantics,
- controlled migration to an external framework later.

Tradeoff:
- more initial interfaces must be maintained by this repository.
