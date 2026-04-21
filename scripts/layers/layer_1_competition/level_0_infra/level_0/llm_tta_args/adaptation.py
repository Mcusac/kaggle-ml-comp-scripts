from typing import Any


def add_llm_tta_adaptation(parser: Any) -> None:
    parser.add_argument("--llm-adapt-steps", type=int, default=0)
    parser.add_argument("--llm-adapt-batch-size", type=int, default=1)

    parser.add_argument("--llm-adapt-gradient-accumulation-steps", type=int, default=1)

    parser.add_argument("--llm-adapt-disabled", action="store_true")

    parser.add_argument(
        "--llm-per-task-adaptation",
        action="store_true",
    )
