from __future__ import annotations

import json

from pathlib import Path


_MIN_TASK = {
    "train": [{"input": [[0, 1], [1, 0]], "output": [[1, 0], [0, 1]]}],
    "test": [{"input": [[0, 1], [1, 0]]}],
}


def _write_min_arc_dataset(root: Path) -> None:
    payload = {"t0": _MIN_TASK}
    for name in (
        "arc-agi_training_challenges.json",
        "arc-agi_evaluation_challenges.json",
        "arc-agi_test_challenges.json",
    ):
        with (root / name).open("w", encoding="utf-8") as f:
            json.dump(payload, f)


def test_arc_validate_pipeline_returns_failure_without_raising(tmp_path: Path) -> None:
    # Import inside test to reuse the tests' sys.path bootstrap.
    from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_3.orchestration import (
        run_validate_data_pipeline,
    )

    # Empty directory exists but is missing required ARC files -> validation should fail.
    result = run_validate_data_pipeline(data_root=str(tmp_path), max_targets=0, run_ctx=None)
    assert result.success is False
    assert result.stage == "validate_data"
    assert result.error


def test_arc_train_pipeline_short_circuits_on_validation_failure(tmp_path: Path) -> None:
    from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_3.orchestration import (
        run_train_pipeline_result,
    )

    result = run_train_pipeline_result(
        data_root=str(tmp_path),
        train_mode="end_to_end",
        models=["baseline_approx"],
        max_targets=0,
        run_ctx=None,
        validate_first=True,
    )
    assert result.success is False
    assert result.stage == "train"
    assert result.error
    assert dict(result.metadata).get("blocked_by") == "validate_data"


def test_train_and_submit_returns_train_stage_when_train_raises(tmp_path: Path, monkeypatch) -> None:
    _write_min_arc_dataset(tmp_path)

    def _boom(*_a, **_k):
        raise RuntimeError("train boom")

    monkeypatch.setattr(
        "layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.stages.run_train_pipeline",
        _boom,
    )
    from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_3.orchestration import (
        run_train_and_submit_pipeline_result,
    )

    result = run_train_and_submit_pipeline_result(
        data_root=str(tmp_path),
        train_mode="end_to_end",
        models=["baseline_approx"],
        strategy="single",
        max_targets=0,
        run_ctx=None,
        validate_first=True,
    )
    assert result.success is False
    assert result.stage == "train"
    assert "train boom" in (result.error or "")


def test_submit_default_uses_copy_input_attempt(tmp_path: Path) -> None:
    _write_min_arc_dataset(tmp_path)
    out = tmp_path / "submission.json"
    from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.stages import run_submission_pipeline

    run_submission_pipeline(
        str(tmp_path),
        "single",
        output_json=str(out),
        max_targets=0,
        run_ctx=None,
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    inp = _MIN_TASK["test"][0]["input"]
    assert data["t0"][0]["attempt_1"] == inp
    assert data["t0"][0]["attempt_2"] == [[0, 0], [0, 0]]


def test_submit_respects_tuned_blank_grid(tmp_path: Path) -> None:
    _write_min_arc_dataset(tmp_path)
    tuned = tmp_path / "best_config.json"
    tuned.write_text(
        json.dumps({"chosen_params": {"heuristic": "blank_grid", "version": 1}}),
        encoding="utf-8",
    )
    out = tmp_path / "submission2.json"
    from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.stages import run_submission_pipeline

    run_submission_pipeline(
        str(tmp_path),
        "single",
        output_json=str(out),
        max_targets=0,
        run_ctx=None,
        tuned_config_path=str(tuned),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    z = [[0, 0], [0, 0]]
    assert data["t0"][0]["attempt_1"] == z
    assert data["t0"][0]["attempt_2"] == z


def test_predict_attempts_unknown_heuristic_falls_back() -> None:
    from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.solvers import (
        predict_attempts_from_chosen_params,
    )

    inp = [[1, 2], [3, 4]]
    a1, a2 = predict_attempts_from_chosen_params(inp, {"heuristic": "not_a_real_heuristic"})
    assert a1 == inp
    assert a2 == [[0, 0], [0, 0]]

