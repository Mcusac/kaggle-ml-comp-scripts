"""Deterministic mock LM backend for environments without LM dependencies."""

from typing import Any

from layers.layer_1_competition.level_0_infra.level_0.lm import LmAdaptationConfig

from .protocol import Grid, LmBackend, LmBackendConfig


class MockLmBackend(LmBackend):
    """Deterministic backend for environments without LM dependencies."""

    def __init__(self, config: LmBackendConfig) -> None:
        self._config = config
        self._loaded = False

    def backend_name(self) -> str:
        return "mock"

    def is_available(self) -> bool:
        return True

    def load(self) -> None:
        self._loaded = True

    def adapt_for_task(
        self,
        task_payload: dict[str, Any],
        budget_expired: callable,
        *,
        adaptation: LmAdaptationConfig | None = None,
    ) -> dict[str, Any]:
        return {"status": "ok", "steps": 0, "backend": "mock"}

    def infer_cell_probs(self, input_grid: Grid) -> list[list[list[float]]]:
        h = len(input_grid)
        w = len(input_grid[0]) if h else 0
        out = [[[1e-4 for _ in range(10)] for _ in range(w)] for _ in range(h)]
        for r in range(h):
            for c in range(w):
                color = int(input_grid[r][c]) % 10
                out[r][c][color] = 0.9
        return out

    def score_candidate_grid(self, task_payload: dict[str, Any], candidate_grid: Grid) -> float:
        train = task_payload.get("train", []) if isinstance(task_payload, dict) else []
        if not isinstance(train, list):
            return 0.0
        score = 0.0
        for pair in train:
            if not isinstance(pair, dict):
                continue
            out = pair.get("output")
            if not isinstance(out, list):
                continue
            same = 0
            total = 0
            for r in range(min(len(out), len(candidate_grid))):
                for c in range(min(len(out[r]), len(candidate_grid[r]))):
                    total += 1
                    if int(out[r][c]) == int(candidate_grid[r][c]):
                        same += 1
            if total > 0:
                score += float(same) / float(total)
        return float(score)

    def get_tokenizer(self) -> Any | None:
        return None

    def turbo_dfs_beams(
        self,
        prefix_token_ids: list[int],
        max_new_tokens: int,
        max_score: float,
        end_time: float,
        *,
        inner_loop_wall_sec: float | None = None,
    ) -> list[tuple[float, list[int]]]:
        return []