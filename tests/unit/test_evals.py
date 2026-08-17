from pathlib import Path

from autonomous_dataops.models import EvalCase


def test_phase_one_eval_cases_follow_typed_contract() -> None:
    lines = Path("evals/datasets/sample_cases.jsonl").read_text(encoding="utf-8").splitlines()
    cases = [
        EvalCase.model_validate_json(line)
        for line in lines
        if line.strip()
    ]
    assert cases
    assert all(case.expected.required_stages for case in cases)
    assert all(case.expected.forbidden_actions for case in cases)
    assert all(case.expected.minimum_evidence_per_stage >= 1 for case in cases)
