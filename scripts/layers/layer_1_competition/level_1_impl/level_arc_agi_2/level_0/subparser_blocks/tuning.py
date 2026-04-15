from typing import Any


def add_search_type(parser: Any, default: str = "quick") -> None:
    parser.add_argument(
        "--search-type",
        choices=["quick", "thorough"],
        default=default,
        help="Hyperparameter search mode",
    )