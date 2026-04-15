from typing import Any


def add_llm_tta_core(parser: Any) -> None:
    parser.add_argument(
        "--llm-execution-mode",
        choices=("surrogate", "lm_backend"),
        default="surrogate",
        help="llm_tta_dfs execution mode.",
    )

    parser.add_argument(
        "--llm-enable-neural-backend",
        action="store_true",
        help="Enable neural backend path when available.",
    )