"""Qwen-style chat strings for ARC digit grids (reference notebook ``QwenFormatter`` pattern)."""

from dataclasses import dataclass
from typing import Any

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    MAX_ARC_GRID_DIM,
    arc_grid_to_text_lines,
    arc_text_lines_to_grid,
)

Grid = list[list[int]]


@dataclass
class ArcQwenGridChatFormatter:
    """Build user/assistant chat segments for newline-digit ARC grids (Qwen chat template style)."""

    tokenizer: Any
    im_user: str = "<|im_start|>user\n"
    im_assistant: str = "<|im_start|>assistant\n"
    im_end: str = "<|im_end|>"

    def fmt_query_from_input_grid(self, input_grid: Grid) -> str:
        grid_input = arc_grid_to_text_lines(input_grid)
        return self.im_user + grid_input + self.im_end + self.im_assistant

    def fmt_reply_from_output_grid(self, output_grid: Grid) -> str:
        return arc_grid_to_text_lines(output_grid) + self.im_end

    def fmt_train_block(
        self,
        train_pairs: list[dict[str, Grid]],
        *,
        last_is_challenge: bool = False,
    ) -> str:
        """Concatenate train pairs; optional trailing query+reply for challenge (last pair)."""
        text = ""
        pairs = list(train_pairs)
        test_query: Grid | None = None
        test_output: Grid | None = None
        if last_is_challenge and pairs:
            last = pairs[-1]
            inp = last.get("input")
            out = last.get("output")
            if isinstance(inp, list) and isinstance(out, list):
                test_query = inp
                test_output = out
            pairs = pairs[:-1]
        for x in pairs:
            gi = x.get("input")
            go = x.get("output")
            if not isinstance(gi, list) or not isinstance(go, list):
                continue
            grid_input = arc_grid_to_text_lines(gi)
            grid_output = arc_grid_to_text_lines(go)
            text += (
                self.im_user + grid_input + self.im_end + self.im_assistant + grid_output + self.im_end
            )
        if test_query is not None and test_output is not None:
            text += self.fmt_query_from_input_grid(test_query) + self.fmt_reply_from_output_grid(test_output)
        return text

    def max_new_tokens_for_max_grid(self) -> int:
        max_grid = [[0 for _ in range(MAX_ARC_GRID_DIM)] for _ in range(MAX_ARC_GRID_DIM)]
        tok = self.tokenizer.encode(self.fmt_reply_from_output_grid(max_grid))
        return len(tok) + 1

    def decode_tokens_to_grid(self, tokens: list[int], *, limit_rows: int = MAX_ARC_GRID_DIM) -> Grid | None:
        if len(tokens) < 2:
            return None
        try:
            text = self.tokenizer.decode(tokens[:-1])
        except Exception:
            return None
        return arc_text_lines_to_grid(text, limit_rows=limit_rows)


def arc_count_tokens(formatter: ArcQwenGridChatFormatter, text: str) -> int:
    """Encode length for budget checks (uses ``tokenizer.encode``)."""
    try:
        return len(formatter.tokenizer.encode(text))
    except Exception:
        return 0
