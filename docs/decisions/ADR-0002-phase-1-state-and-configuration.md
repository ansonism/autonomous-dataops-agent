# ADR-0002: Use strict typed boundaries and repository-backed checkpoints

**Status:** Accepted

## Context

Phase 1 requires validated configuration, domain-specific run state, resumability, and
structured observability while retaining provider-neutral deterministic execution. The Phase
0 scaffold used unvalidated dictionaries for configuration and incident state and kept no
checkpoint after a process exited.

## Decision

- Validate YAML plus `DATAOPS__SECTION__FIELD` environment overrides into strict Pydantic
  settings models. Unknown keys and unsafe approval combinations fail before a run begins.
- Convert incident JSON into a strict `IncidentInput` at the CLI boundary and use typed models
  throughout the workflow.
- Define a provider-neutral `RunStateRepository`, with an in-memory implementation for unit
  tests and atomic local JSON files for the CLI.
- Save a checkpoint after initial state, each completed stage, and final status. Resuming the
  same run skips completed stages and rejects changed incident input.
- Emit redacted JSON log events at stage and run boundaries. Provider usage is represented by
  a domain model rather than vendor SDK types.

## Consequences

Local runs are inspectable and resumable, and invalid boundary data fails early. State schema
changes now require explicit migration consideration. Local JSON is appropriate for one-process
development but does not provide distributed locking; a later persistence phase can add SQLite
or PostgreSQL behind the same interface.
