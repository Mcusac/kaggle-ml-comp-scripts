from typing import Any


def add_run_context(parser: Any) -> None:
    """
    Standard run metadata for reproducibility + logging.
    """
    parser.add_argument("--run-id", type=str, help="Optional run id for run folder tracking")
    parser.add_argument("--run-dir", type=str, help="Optional explicit run folder path")