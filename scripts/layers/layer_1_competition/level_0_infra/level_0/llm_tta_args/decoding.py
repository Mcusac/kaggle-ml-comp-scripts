from typing import Any


def add_llm_tta_decoding(parser: Any) -> None:
    parser.add_argument("--llm-beam-width", type=int, default=12)
    parser.add_argument("--llm-max-candidates", type=int, default=6)

    parser.add_argument("--llm-max-neg-log-score", type=float, default=120.0)
