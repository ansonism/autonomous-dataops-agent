# Autonomous DataOps Agent

    A safety-first DataOps control plane that observes data-platform health, diagnoses incidents, plans remediations, verifies proposed changes, requests approval, executes through adapters, validates outcomes, and supports rollback.

    ## Why this exists

    Coordinate specialized agents to reduce data-platform MTTR while preserving human control, change safety, evidence trails, idempotency, and rollback capability.

    This repository is intentionally scaffolded as a **production-oriented agent project**, not a prompt-only demo. It starts with a deterministic mock provider so the complete orchestration path can be executed locally before adding any commercial LLM.

    ## Core workflow

    observe_and_detect -> triage_and_classify -> diagnose_with_specialists -> plan_remediation -> verify_plan_and_simulate -> risk_score_and_gate -> request_human_approval -> execute_via_controlled_adapter -> validate_outcome -> rollback_if_required -> record_incident_and_learning

    ## Specialized agents

    - `observer`
- `incident_commander`
- `rca_agent`
- `data_quality_specialist`
- `schema_specialist`
- `lineage_specialist`
- `security_guard`
- `remediation_planner`
- `change_verifier`
- `execution_controller`
- `validation_agent`

    ## Planned tool adapters

    - `alert_reader`
- `log_reader`
- `metric_reader`
- `orchestrator_adapter`
- `git_adapter`
- `data_platform_adapter`
- `approval_gateway`
- `audit_writer`

    ## Quick start

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -e ".[dev]"
    autonomous-dataops run examples/sample_input.json --output out/result.json
    pytest
    ```

    Or:

    ```bash
    make setup
    make demo
    make test
    ```

    ## Safety defaults

    - Mock/dry-run behavior is the default.
    - External systems are accessed only through explicit adapters.
    - No production mutation should be added without an approval gate.
    - Facts, assumptions, hypotheses and recommendations should remain distinguishable in outputs.
    - Credentials must come from environment/secret stores, never source control.

    ## Codex implementation guide

    Start with [`SKILL.md`](./SKILL.md). It defines the mission, architecture, implementation sequence, acceptance criteria and guardrails Codex should follow.

    ## Repository layout

    ```text
    .
    ├── AGENTS.md
    ├── SKILL.md
    ├── config/
    ├── docs/
    ├── evals/
    ├── examples/
    ├── kubernetes/
    ├── prompts/
    ├── scripts/
    ├── src/autonomous_dataops/
    ├── terraform/
    └── tests/
    ```

    ## Current state

    **Phase 1 core.** The typed harness runs end-to-end with a deterministic mock provider. It
    validates configuration and incident inputs, writes an atomic checkpoint after every stage,
    supports idempotent resume by run ID in the Python API, and emits redacted structured logs.

    The default CLI stores checkpoints in `out/state/`. Configuration can be overridden with
    typed environment variables such as `DATAOPS__PROVIDER__MAX_RETRIES=3`; nested names use
    double underscores. Unknown configuration or incident fields fail fast.

    `make demo`, `make test`, and `make lint` are the Phase 1 verification commands. The test
    target enforces at least 80% coverage of the core package.
