"""Forward-pass inference mixin shared by Transformers and Unsloth backends.

Concerns: cell-probability inference, turbo DFS beams, candidate grid scoring.
No decoding policy lives here — policy choices stay in the concrete backends.
"""

from typing import Any

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    arc_grid_to_text_lines,
    eval_teacher_forced_neg_sum_logprob,
    REFERENCE_INNER_LOOP_WALL_SEC,
    inference_turbo_dfs,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import (
    ArcQwenGridChatFormatter,
)

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2 import (
    resolve_arc_digit_token_ids,
    resolve_newline_token_id,
    resolve_turbo_arc_token_table,
)

Grid = list[list[int]]


class SharedTorchLmInference:
    """Forward-pass inference shared by Transformers and Unsloth backends (no decoding policy)."""

    _loaded: bool
    _torch: Any
    _model: Any
    _tokenizer: Any

    def get_tokenizer(self) -> Any | None:
        return self._tokenizer

    def turbo_dfs_beams(
        self,
        prefix_token_ids: list[int],
        max_new_tokens: int,
        max_score: float,
        end_time: float,
        *,
        inner_loop_wall_sec: float | None = None,
    ) -> list[tuple[float, list[int]]]:
        """Run ``inference_turbo_dfs`` for batch row 0; returns ``[(beam_nll, token_ids), ...]`` sorted by NLL."""
        if not self._loaded or self._model is None or self._tokenizer is None:
            raise RuntimeError("LM backend not loaded; call load() before turbo_dfs_beams().")

        fmt = ArcQwenGridChatFormatter(tokenizer=self._tokenizer)
        arc_tokens, pad_id, eos_id = resolve_turbo_arc_token_table(self._tokenizer, fmt)
        wall = float(inner_loop_wall_sec) if inner_loop_wall_sec is not None else float(REFERENCE_INNER_LOOP_WALL_SEC)
        raw = inference_turbo_dfs(
            self._model,
            prefix_token_ids,
            int(max_new_tokens),
            float(max_score),
            float(end_time),
            inner_loop_wall_sec=wall,
            arc_tokens=arc_tokens,
            pad_id=pad_id,
            eos_id=eos_id,
        )
        for bid, beams in raw:
            if int(bid) == 0:
                return [(float(s), list(toks)) for s, toks in beams]
        return []

    def infer_cell_probs(self, input_grid: Grid) -> list[list[list[float]]]:
        """Infer per-cell digit probabilities from a real LM forward pass.

        Returns an ``[H][W][10]`` list structure aligned with `llm_tta_runner`'s
        prefix indexing (prefix length == cell index). This does not implement
        DFS/beam search yet; it uses a greedy rollout to condition later cells.
        """
        if not self._loaded or self._model is None or self._tokenizer is None or self._torch is None:
            raise RuntimeError("LM backend not loaded; call load() before infer_cell_probs().")

        torch = self._torch
        model = self._model
        tokenizer = self._tokenizer

        h = len(input_grid)
        w = len(input_grid[0]) if h else 0
        if h <= 0 or w <= 0:
            return []

        device = next(model.parameters()).device
        formatter = ArcQwenGridChatFormatter(tokenizer=tokenizer)
        prompt = formatter.fmt_query_from_input_grid(input_grid)
        prompt_ids = tokenizer.encode(prompt, add_special_tokens=False)
        if not isinstance(prompt_ids, list) or not prompt_ids:
            raise RuntimeError("Tokenization produced empty prompt ids.")

        digit_token_ids = resolve_arc_digit_token_ids(tokenizer)
        newline_token_id = resolve_newline_token_id(tokenizer)

        out: list[list[list[float]]] = [[[0.0 for _ in range(10)] for _ in range(w)] for _ in range(h)]
        generated_ids: list[int] = []

        with torch.no_grad():
            for r in range(h):
                for c in range(w):
                    input_ids = torch.tensor([prompt_ids + generated_ids], device=device, dtype=torch.long)
                    outputs = model(input_ids=input_ids, return_dict=True, use_cache=False)
                    logits = outputs.logits[0, -1, :]
                    probs = torch.softmax(logits.float(), dim=-1)
                    digit_probs = [float(probs[int(tid)].item()) for tid in digit_token_ids]

                    s = float(sum(digit_probs))
                    if s <= 0.0:
                        digit_probs = [0.1] * 10
                        s = 1.0
                    digit_probs = [float(p / s) for p in digit_probs]
                    out[r][c] = digit_probs

                    best_color = max(range(10), key=lambda i: digit_probs[i])
                    generated_ids.append(int(digit_token_ids[int(best_color)]))
                generated_ids.append(int(newline_token_id))

        return out

    def score_candidate_grid(self, task_payload: dict[str, Any], candidate_grid: Grid) -> float:
        if not self._loaded or self._model is None or self._tokenizer is None:
            return 0.0

        device = next(self._model.parameters()).device
        answer = arc_grid_to_text_lines(candidate_grid)
        qtxt = ""
        if getattr(self._tokenizer, "bos_token", None):
            qtxt = str(self._tokenizer.bos_token)
        nll = eval_teacher_forced_neg_sum_logprob(
            model=self._model,
            tokenizer=self._tokenizer,
            query_text=qtxt,
            answer_text=answer,
            device=device,
        )
        if nll is None:
            return 0.0
        return float(-nll)
