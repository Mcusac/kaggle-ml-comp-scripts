"""Per-augmentation decode branch implementations for LLM-TTA DFS.

Three mutually exclusive strategies producing a list of candidate objects with
``.grid`` and ``.score`` attributes. The ``type("Tmp", ...)`` anonymous wrappers
are preserved verbatim from the pre-refactor runner to guarantee identical
downstream behavior (post-decode inversion + scoring + ranking).
"""

from typing import Any, Mapping

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    ArcLmBudget,
    LlmTtaDfsConfig,
    apply_augmentation,
    build_cell_probs_from_support_grids,
    collect_llm_tta_support_grids,
    decode_grid_candidates,
    decode_tokens_to_grids,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import (
    ArcQwenGridChatFormatter,
    turbo_wall_end_time,
)


def decode_with_cell_probs(
    aug_input: list[list[int]],
    lm_probs: list[list[list[float]]],
    ah: int,
    aw: int,
    config: LlmTtaDfsConfig,
) -> list[Any]:
    """Cell-probs surrogate decode (no tokenizer; uses fixed 10-class per-cell probs)."""
    probs = lm_probs
    decoded = decode_tokens_to_grids(
        input_grid=aug_input,
        token_probs_provider=lambda _prefix: {
            i: probs[min(len(_prefix) // max(1, aw), ah - 1)][len(_prefix) % max(1, aw)][i]
            for i in range(10)
        },
        beam_width=int(config.beam_width or 1),
        max_candidates=int(config.max_candidates or 1),
        max_neg_log_score=float(config.max_neg_log_score or 120.0),
    )
    decoded = [type("Tmp", (), {"grid": cand.grid, "score": cand.score}) for cand in decoded]
    return decoded


def decode_with_turbo_lm(
    aug_input: list[list[int]],
    lm_backend: Any,
    config: LlmTtaDfsConfig,
    budget: ArcLmBudget,
) -> list[Any]:
    """Turbo LM DFS beams via the chat-formatted prompt + tokenizer."""
    tok = lm_backend.get_tokenizer()
    fmt = ArcQwenGridChatFormatter(tokenizer=tok)
    prompt = fmt.fmt_query_from_input_grid(aug_input)
    raw_ids = tok.encode(prompt, add_special_tokens=False)
    if hasattr(raw_ids, "tolist"):
        prefix_ids = [int(x) for x in raw_ids.tolist()]
    elif isinstance(raw_ids, list):
        prefix_ids = [int(x) for x in raw_ids]
    else:
        prefix_ids = [int(x) for x in list(raw_ids)]
    max_nt = (
        int(config.turbo_max_new_tokens)
        if config.turbo_max_new_tokens is not None
        else int(fmt.max_new_tokens_for_max_grid() + 1)
    )
    end_wall = turbo_wall_end_time(budget)
    beams = lm_backend.turbo_dfs_beams(
        list(prefix_ids),
        max_nt,
        float(config.turbo_prune_max_nll),
        end_wall,
        inner_loop_wall_sec=config.turbo_inner_loop_wall_sec,
    )
    mc = max(1, int(config.max_candidates or 1))
    decoded: list[Any] = []
    for nll, suffix in beams[:mc]:
        full_ids = list(prefix_ids) + list(suffix)
        grid = fmt.decode_tokens_to_grid(full_ids)
        if grid is None:
            continue
        decoded.append(type("Tmp", (), {"grid": grid, "score": float(-nll)})())
    return decoded


def decode_with_support_grids(
    aug_input: list[list[int]],
    base_input: list[list[int]],
    spec: Any,
    task_payload: Mapping[str, Any] | None,
    ah: int,
    aw: int,
    config: LlmTtaDfsConfig,
) -> list[Any]:
    """Support-grid cell probs fallback (no LM; derives per-cell probs from neighbors)."""
    raw_support = collect_llm_tta_support_grids(task_payload, base_input)
    support = [apply_augmentation(sg, spec) for sg in raw_support]
    if not support:
        support = [aug_input]
    probs = build_cell_probs_from_support_grids(support, ah, aw)
    decoded = decode_grid_candidates(
        probs,
        beam_width=int(config.beam_width or 1),
        max_candidates=int(config.max_candidates or 1),
        max_neg_log_score=float(config.max_neg_log_score or 120.0),
    )
    return decoded
