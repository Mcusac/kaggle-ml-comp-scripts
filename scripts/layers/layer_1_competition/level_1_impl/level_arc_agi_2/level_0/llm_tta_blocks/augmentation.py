from typing import Any


def add_llm_tta_augmentation(parser: Any) -> None:
    parser.add_argument("--llm-num-augmentations", type=int, default=8)
    parser.add_argument("--llm-seed", type=int, default=0)

    parser.add_argument(
        "--llm-augmentation-likelihood-weight",
        type=float,
        default=1.0,
    )