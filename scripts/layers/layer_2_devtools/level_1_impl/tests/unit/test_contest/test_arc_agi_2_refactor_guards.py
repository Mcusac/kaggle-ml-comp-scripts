"""Regression guards for ARC refactor: solution JSON parsing and decoding parity."""

from __future__ import annotations


def test_eval_parse_task_solution_grids_shapes() -> None:
    from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.decoding.eval_solution_parse import (
        eval_parse_task_solution_grids,
    )

    # Missing task
    assert eval_parse_task_solution_grids({}, "t1", 2) == [None, None]

    # List of grids per test
    sols = {"t1": [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]}
    g = eval_parse_task_solution_grids(sols, "t1", 2)
    assert g[0] == [[1, 2], [3, 4]]
    assert g[1] == [[5, 6], [7, 8]]

    # Single grid as nested list (one test output)
    sols2 = {"t2": [[0, 1], [1, 0]]}
    g2 = eval_parse_task_solution_grids(sols2, "t2", 3)
    assert g2[0] == [[0, 1], [1, 0]]
    assert g2[1] is None
    assert g2[2] is None

    # String key fallback
    sols3 = {42: [[[9]]]}
    g3 = eval_parse_task_solution_grids(sols3, "42", 1)
    assert g3[0] == [[9]]


def test_decode_grid_candidates_matches_row_major_cell_probs() -> None:
    """Same [H][W][K] tensor should match decode_grid_candidates directly vs provider path."""
    from layers.layer_1_competition.level_0_infra.level_1.decoding.cell_prob_decoder import (
        decode_grid_candidates,
        decode_grid_candidates_from_provider,
    )

    probs = [
        [[0.9] + [0.1 / 9.0] * 9, [0.05, 0.9] + [0.05 / 8.0] * 8],
        [[0.2] * 5 + [0.0] * 5, [0.1] * 10],
    ]
    direct = decode_grid_candidates(
        probs, beam_width=8, max_candidates=4, max_neg_log_score=80.0
    )

    h, w = 2, 2

    def provider(prefix: list[int]) -> dict[int, float]:
        idx = len(prefix)
        r, c = idx // max(1, w), idx % max(1, w)
        return {i: float(probs[r][c][i]) for i in range(10)}

    via_provider = decode_grid_candidates_from_provider(
        h,
        w,
        provider,
        beam_width=8,
        max_candidates=4,
        max_neg_log_score=80.0,
    )
    assert len(direct) == len(via_provider)
    for a, b in zip(direct, via_provider, strict=True):
        assert a.grid == b.grid
        assert abs(a.score - b.score) < 1e-6
