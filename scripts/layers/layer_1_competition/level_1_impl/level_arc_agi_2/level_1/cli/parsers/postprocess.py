"""Register ``score_submission`` and ``benchmark_rankers`` subparsers."""

from typing import Any

from layers.layer_1_competition.level_0_infra.level_1 import add_common_contest_args


def add_postprocess_subparsers(subparsers: Any) -> None:
    score = subparsers.add_parser(
        "score_submission",
        help="Score a submission CSV against reference solutions",
    )
    add_common_contest_args(score)
    score.add_argument(
        "--submission",
        type=str,
        required=True,
        help="Path to submission JSON/CSV",
    )
    score.add_argument(
        "--split",
        type=str,
        default="evaluation",
        help="Split label (default: evaluation)",
    )

    bench = subparsers.add_parser(
        "benchmark_rankers",
        help="Benchmark rankers from decoded artifact directory",
    )
    add_common_contest_args(bench)
    bench.add_argument(
        "--decoded-dir",
        type=str,
        required=True,
        help="Directory with decoded prediction artifacts",
    )
    bench.add_argument(
        "--split",
        type=str,
        default="evaluation",
        help="Split label (default: evaluation)",
    )
    bench.add_argument(
        "--n-guesses",
        type=int,
        default=2,
        help="Number of guesses per task to evaluate",
    )
    bench.add_argument(
        "--max-targets",
        type=int,
        default=0,
        help="If >0, only evaluate the first N targets",
    )
