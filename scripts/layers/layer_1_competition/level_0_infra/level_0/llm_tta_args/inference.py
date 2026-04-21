from typing import Any


def add_llm_tta_inference(parser: Any) -> None:
    parser.add_argument("--llm-model-path", type=str, default=None)
    parser.add_argument("--llm-lora-path", type=str, default=None)

    parser.add_argument(
        "--llm-candidate-ranker",
        choices=("default", "kgmon", "probmul"),
        default="default",
    )

    parser.add_argument("--llm-prefer-cnn-attempt1", action="store_true")
