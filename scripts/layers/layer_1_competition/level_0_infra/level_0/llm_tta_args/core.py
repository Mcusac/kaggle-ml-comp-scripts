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

    parser.add_argument(
        "--llm-consistency-weight",
        type=float,
        default=1.0,
        help="Weight for augmentation agreement in candidate ranking.",
    )

    parser.add_argument(
        "--llm-model-weight",
        type=float,
        default=1.0,
        help="Weight for model score term in candidate ranking.",
    )
