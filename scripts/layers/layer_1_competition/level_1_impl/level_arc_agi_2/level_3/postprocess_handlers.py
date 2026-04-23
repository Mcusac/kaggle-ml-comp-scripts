"""Post-processing handlers: score_submission, benchmark_rankers."""

import argparse

from layers.layer_0_core.level_0 import get_logger

from layers.layer_1_competition.level_0_infra.level_1 import (
    resolve_data_root_from_args,
)

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2 import (
    pipeline_run_benchmark_rankers_from_artifacts,
    pipeline_run_score_submission,
)

_logger = get_logger(__name__)


def score_submission_cmd(args: argparse.Namespace) -> None:
    try:
        out = pipeline_run_score_submission(
            data_root=resolve_data_root_from_args(args),
            submission_path=str(getattr(args, "submission", "")),
            split=str(getattr(args, "split", "evaluation")),
        )
        _logger.info("✅ score_submission score=%s paths=%s", out.get("score"), {k: out[k] for k in ("challenges_path", "solutions_path", "submission_path")})
    except Exception as e:
        _logger.error("❌ score_submission failed: %s", e)
        raise


def benchmark_rankers_cmd(args: argparse.Namespace) -> None:
    try:
        out = pipeline_run_benchmark_rankers_from_artifacts(
            data_root=resolve_data_root_from_args(args),
            decoded_dir=str(getattr(args, "decoded_dir", "")),
            split=str(getattr(args, "split", "evaluation")),
            n_guesses=int(getattr(args, "n_guesses", 2) or 2),
            max_targets=int(getattr(args, "max_targets", 0) or 0),
        )
        _logger.info("✅ benchmark_rankers summary=%s", out)
    except Exception as e:
        _logger.error("❌ benchmark_rankers failed: %s", e)
        raise
