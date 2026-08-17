# Evaluation plan

    Start with deterministic evals against the mock/fake adapters, then add provider-backed eval runs.

    Domain acceptance targets from `SKILL.md`:

    - Default mode is dry-run; production writes require an explicit approval token.
- Every proposed action has preconditions, postconditions and rollback instructions.
- The verifier can reject the planner's proposal.
- The execution controller only invokes allow-listed tools.
- Incident runs are resumable/idempotent and emit an auditable event stream.
- E2E demo shows detect -> diagnose -> approve -> remediate -> validate against a simulated pipeline.

    Do not use an LLM judge as the sole source of truth for safety-critical or mechanically verifiable assertions.

    Phase 1 cases follow the typed `EvalCase` contract: required and forbidden findings,
    forbidden actions, expected risk range, required stages, and minimum evidence coverage.
    They execute with `MockProvider`; no network access or model judge is required.
