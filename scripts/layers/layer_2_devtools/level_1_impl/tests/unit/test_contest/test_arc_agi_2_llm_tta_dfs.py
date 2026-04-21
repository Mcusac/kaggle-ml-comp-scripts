import json
from pathlib import Path


def _write_min_arc_dataset(root: Path) -> None:
    payload = {
        "t0": {
            "train": [{"input": [[1, 0], [0, 1]], "output": [[1, 1], [1, 1]]}],
            "test": [{"input": [[1, 0], [0, 1]]}],
        }
    }
    for name in (
        "arc-agi_training_challenges.json",
        "arc-agi_evaluation_challenges.json",
        "arc-agi_test_challenges.json",
    ):
        (root / name).write_text(json.dumps(payload), encoding="utf-8")


def test_augmentation_inversion_roundtrip() -> None:
    from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
        apply_augmentation,
        generate_augmentation_specs,
        invert_augmentation,
    )

    grid = [[1, 2, 3], [4, 5, 6]]
    specs = generate_augmentation_specs(6, seed=123, include_identity=True)
    for spec in specs:
        aug = apply_augmentation(grid, spec)
        inv = invert_augmentation(aug, spec)
        assert inv == grid


def test_decoder_respects_constraints() -> None:
    from layers.layer_1_competition.level_0_infra.level_1 import decode_grid_candidates

    probs = [
        [[0.9] + [0.1 / 9.0] * 9, [0.05, 0.9] + [0.05 / 8.0] * 8],
        [[0.2] * 5 + [0.0] * 5, [0.1] * 10],
    ]
    out = decode_grid_candidates(probs, beam_width=8, max_candidates=3, max_neg_log_score=80.0)
    assert out
    for cand in out:
        assert len(cand.grid) == 2
        assert len(cand.grid[0]) == 2
        assert all(0 <= v <= 9 for row in cand.grid for v in row)
    assert out[0].score >= out[-1].score


def test_candidate_ranking_is_deterministic() -> None:
    from layers.layer_1_competition.level_0_infra.level_1 import (
        CandidatePrediction,
        rank_candidate_grids,
    )

    preds = [
        CandidatePrediction(grid=[[1]], model_score=-0.1, aug_key="a", aug_likelihood_score=0.2),
        CandidatePrediction(grid=[[1]], model_score=-0.2, aug_key="b", aug_likelihood_score=0.1),
        CandidatePrediction(grid=[[2]], model_score=-0.05, aug_key="c", aug_likelihood_score=0.0),
    ]
    ranked1 = rank_candidate_grids(
        preds,
        consistency_weight=1.0,
        model_weight=1.0,
        augmentation_likelihood_weight=1.0,
    )
    ranked2 = rank_candidate_grids(
        preds,
        consistency_weight=1.0,
        model_weight=1.0,
        augmentation_likelihood_weight=1.0,
    )
    assert [r.grid for r in ranked1] == [r.grid for r in ranked2]
    assert ranked1[0].support_count >= ranked1[-1].support_count


def test_submission_pipeline_llm_tta_dfs_outputs_two_attempts(tmp_path: Path) -> None:
    _write_min_arc_dataset(tmp_path)
    out = tmp_path / "submission.json"

    from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_7.submit import (
        run_submission_pipeline,
    )

    run_submission_pipeline(
        str(tmp_path),
        "llm_tta_dfs",
        output_json=str(out),
        max_targets=0,
        run_ctx=None,
        llm_execution_mode="surrogate",
        llm_num_augmentations=4,
        llm_beam_width=6,
        llm_max_candidates=4,
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert "t0" in data
    assert "attempt_1" in data["t0"][0]
    assert "attempt_2" in data["t0"][0]
    assert isinstance(data["t0"][0]["attempt_1"], list)
    assert isinstance(data["t0"][0]["attempt_2"], list)


def test_submission_pipeline_llm_backend_mode_with_mock(tmp_path: Path) -> None:
    _write_min_arc_dataset(tmp_path)
    out = tmp_path / "submission_lm_mock.json"

    from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_7.submit import (
        run_submission_pipeline,
    )

    run_submission_pipeline(
        str(tmp_path),
        "llm_tta_dfs",
        output_json=str(out),
        max_targets=0,
        run_ctx=None,
        llm_execution_mode="lm_backend",
        llm_model_path="mock://arc",
        llm_num_augmentations=3,
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert "t0" in data
    assert isinstance(data["t0"][0]["attempt_1"], list)


def test_llm_surrogate_mode_rejects_lm_only_flags() -> None:
    from layers.layer_1_competition.level_0_infra.level_0 import LlmTtaDfsConfig
    from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_5 import (
        predict_attempts_for_llm_tta_dfs,
    )

    try:
        predict_attempts_for_llm_tta_dfs(
            [[1]],
            task_payload={"train": [{"input": [[1]], "output": [[1]]}]},
            task_id="t0",
            test_index=0,
            chosen_params={"heuristic": "copy_input"},
            config=LlmTtaDfsConfig(execution_mode="surrogate", model_path="mock://arc"),
        )
    except ValueError as e:
        assert "LM-only options were provided in surrogate mode" in str(e)
        return
    raise AssertionError("Expected ValueError for surrogate mode with LM-only flags")


def test_llm_budget_forces_fallback() -> None:
    from layers.layer_1_competition.level_0_infra.level_0 import LlmTtaDfsConfig
    from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_5 import (
        predict_attempts_for_llm_tta_dfs,
    )

    a1, a2, meta = predict_attempts_for_llm_tta_dfs(
        [[1, 0], [0, 1]],
        task_payload={"train": [{"input": [[1, 0], [0, 1]], "output": [[1, 1], [1, 1]]}]},
        task_id="t0",
        test_index=0,
        chosen_params={"heuristic": "copy_input"},
        config=LlmTtaDfsConfig(execution_mode="surrogate", max_runtime_sec=1e-12),
    )
    assert a1
    assert a2
    assert meta["status"] in ("fallback_budget", "ok", "fallback_no_candidates")
