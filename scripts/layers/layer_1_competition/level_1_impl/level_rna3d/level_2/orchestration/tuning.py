"""RNA3D hyperparameter tuning using validation TM-score."""

import numpy as np
import pandas as pd

from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Optional

from layers.layer_0_core.level_0 import ensure_dir, get_logger

from layers.layer_1_competition.level_1_impl.level_rna3d.level_0 import RNA3DPaths
from layers.layer_1_competition.level_1_impl.level_rna3d.level_1 import (
    BaselineApproxConfig,
    evaluate_predictions_tm,
    run_baseline_approx_predictions,
)
from layers.layer_1_competition.level_0_infra.level_0.artifacts import write_json
from layers.layer_1_competition.level_0_infra.level_0 import contest_models_dir

logger = get_logger(__name__)


def _get_baseline_approx_grid(search_type: str = "quick") -> List[BaselineApproxConfig]:
    """Build a discrete grid of ``BaselineApproxConfig`` for search_type."""
    if search_type == "quick":
        grid = []
        for template_pool in [60, 80, 100]:
            for template_top_n in [3, 5, 7]:
                for noise_gain in [0.20, 0.25, 0.30]:
                    grid.append(
                        BaselineApproxConfig(
                            template_pool=template_pool,
                            template_top_n=template_top_n,
                            noise_gain=noise_gain,
                        )
                    )
        return grid
    if search_type == "thorough":
        grid = []
        for template_pool in [50, 60, 70, 80, 90, 100]:
            for template_top_n in [3, 5, 7, 10]:
                for noise_gain in [0.15, 0.20, 0.25, 0.30]:
                    for rel_len_cap in [0.25, 0.30, 0.35]:
                        grid.append(
                            BaselineApproxConfig(
                                template_pool=template_pool,
                                template_top_n=template_top_n,
                                noise_gain=noise_gain,
                                rel_len_cap=rel_len_cap,
                            )
                        )
        return grid
    raise ValueError(f"Unknown search_type: {search_type}")


def _predict_validation_baseline_approx(
    data_root: str,
    config: BaselineApproxConfig,
    max_targets: int = 0,
) -> Dict[str, np.ndarray]:
    """Run baseline_approx on validation_sequences.csv."""
    root = Path(data_root)
    validation_sequences_path = root / "validation_sequences.csv"

    if not validation_sequences_path.exists():
        raise FileNotFoundError(f"validation_sequences.csv not found in {data_root}")

    validation_seqs = pd.read_csv(validation_sequences_path, usecols=["target_id", "sequence"])

    return run_baseline_approx_predictions(
        data_root=data_root,
        config=config,
        sequences_df=validation_seqs,
        max_targets=max_targets,
    )


def tune_pipeline(
    data_root: str,
    model_name: str,
    search_type: str = "quick",
    max_targets: int = 0,
) -> Dict:
    """Grid-search hyperparameters on validation data; save best config as JSON.

    Args:
        data_root: Directory with validation_labels.csv and validation_sequences.csv.
        model_name: Currently only ``baseline_approx`` is supported.
        search_type: ``quick`` or ``thorough``.
        max_targets: If > 0, evaluate on the first N validation targets only.

    Returns:
        Dict suitable for JSON (includes ``_tune_score`` and ``_tune_search_type``).
    """
    root = Path(data_root)
    validation_labels_path = root / "validation_labels.csv"

    if not validation_labels_path.exists():
        raise FileNotFoundError(f"validation_labels.csv not found in {data_root}")

    validation_labels = pd.read_csv(validation_labels_path)

    if model_name != "baseline_approx":
        raise ValueError(f"Tuning not yet implemented for model: {model_name}")

    logger.info("Tuning %s with search_type=%s", model_name, search_type)
    grid = _get_baseline_approx_grid(search_type=search_type)
    logger.info("  Grid size: %d candidates", len(grid))

    best_score = -1.0
    best_config: Optional[BaselineApproxConfig] = None
    best_idx = -1

    for idx, cfg in enumerate(grid, start=1):
        logger.info(
            "  Evaluating config %d/%d: pool=%s, top_n=%s, noise=%s",
            idx, len(grid), cfg.template_pool, cfg.template_top_n, cfg.noise_gain,
        )

        try:
            predictions = _predict_validation_baseline_approx(
                data_root=data_root,
                config=cfg,
                max_targets=max_targets,
            )

            mean_tm, _ = evaluate_predictions_tm(
                predictions=predictions,
                labels=validation_labels,
            )

            logger.info("    TM-score: %.4f", mean_tm)

            if mean_tm > best_score:
                best_score = mean_tm
                best_config = cfg
                best_idx = idx

        except Exception as e:
            logger.warning("    Failed: %s", e)
            continue

    if best_config is None:
        raise RuntimeError("No valid config found during tuning")

    logger.info("Best config (idx=%d): TM-score=%.4f", best_idx, best_score)
    logger.info("  template_pool=%s", best_config.template_pool)
    logger.info("  template_top_n=%s", best_config.template_top_n)
    logger.info("  noise_gain=%s", best_config.noise_gain)

    best_dict = asdict(best_config)
    best_dict["_tune_score"] = float(best_score)
    best_dict["_tune_search_type"] = search_type

    paths = RNA3DPaths()
    output_dir = contest_models_dir(paths, "rna3d") / model_name
    ensure_dir(output_dir)
    config_path = output_dir / "best_config.json"

    write_json(config_path, best_dict, indent=2, ensure_ascii=False)

    logger.info("Saved best config: %s", config_path)

    return best_dict
