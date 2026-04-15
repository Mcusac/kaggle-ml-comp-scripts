from typing import Any


def add_llm_tta_runtime(parser: Any) -> None:
    parser.add_argument("--llm-max-runtime-sec", type=float, default=0.0)
    parser.add_argument("--llm-task-runtime-sec", type=float, default=0.0)
    parser.add_argument("--llm-decode-runtime-sec", type=float, default=0.0)

    parser.add_argument(
        "--llm-runtime-attention-mode",
        choices=("auto", "eager", "sdpa"),
        default="auto",
    )

    parser.add_argument("--llm-runtime-disable-compile", action="store_true")

    parser.add_argument(
        "--llm-runtime-allocator-expandable-segments",
        action="store_true",
        default=True,
    )

    parser.add_argument("--llm-runtime-allocator-max-split-size-mb", type=int, default=0)