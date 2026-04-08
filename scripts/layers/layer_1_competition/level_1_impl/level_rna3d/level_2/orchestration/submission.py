"""RNA3D submission pipeline: single, ensemble, and stacking strategies."""

import numpy as np
import pandas as pd

from pathlib import Path
from typing import Dict, List, Optional

from layers.layer_0_core.level_0 import (
    combine_predictions_weighted_average,
    fit_stacking_weights_from_scores,
    get_logger,
)
from layers.layer_0_core.level_4 import load_best_config_json

from layers.layer_1_competition.level_1_impl.level_rna3d.level_0 import validate_rna3d_inputs
from layers.layer_1_competition.level_1_impl.level_rna3d.level_1 import (
    BaselineApproxConfig,
    evaluate_predictions_tm,
    format_predictions_to_submission_csv,
    run_baseline_approx_predictions,
)
from layers.layer_1_competition.level_0_infra.level_1.contest import ValidateFirstRunner
from layers.layer_1_competition.level_0_infra.level_0.submission import validate_strategy_models

logger = get_logger(__name__)


def _predict_baseline_approx(
    data_root: str,
    config: BaselineApproxConfig,
    test_sequences: pd.DataFrame,
) -> Dict[str, np.ndarray]:
    """Run baseline_approx and return target_id -> (L, n_structures, 3) arrays."""
    return run_baseline_approx_predictions(
        data_root=data_root,
        config=config,
        sequences_df=test_sequences,
        max_targets=0,
    )


def _load_model_config(model_name: str, model_dir: Optional[str] = None) -> BaselineApproxConfig:
    """Load ``BaselineApproxConfig`` from ``best_config.json`` when present."""
    if model_dir:
        config_path = Path(model_dir) / "best_config.json"
        if config_path.exists():
            cfg_dict = load_best_config_json(config_path, drop_keys=("score",))
            return BaselineApproxConfig(**cfg_dict)

    return BaselineApproxConfig()


def _fit_stacking_weights(
    predictions_list: List[Dict[str, np.ndarray]],
    validation_labels: pd.DataFrame,
) -> List[float]:
    """Fit nonnegative weights from validation TM-scores."""
    if len(predictions_list) < 2:
        return [1.0] if predictions_list else []

    model_scores: List[float] = []
    for preds in predictions_list:
        mean_tm, _ = evaluate_predictions_tm(
            predictions=preds,
            labels=validation_labels,
        )
        model_scores.append(mean_tm)

    weights = fit_stacking_weights_from_scores(
        np.array(model_scores, dtype=np.float32),
        temperature=2.0,
    )
    return weights.tolist()


def submit_pipeline(
    data_root: str,
    strategy: str,
    models: List[str],
    output_csv: Optional[str] = None,
    max_targets: int = 0,
    model_configs: Optional[Dict[str, BaselineApproxConfig]] = None,
    ensemble_weights: Optional[List[float]] = None,
    use_validation_for_stacking: bool = True,
    *,
    validate_first: bool = True,
) -> Path:
    """Build a submission CSV using ``strategy`` and ``models``.

    Args:
        data_root: Directory containing competition CSVs.
        strategy: ``single``, ``ensemble``, or ``stacking``.
        models: Model names (e.g. ``[\"baseline_approx\"]``).
        output_csv: Optional output path.
        max_targets: If > 0, keep only the first N test targets.
        model_configs: Optional map model_name -> config.
        ensemble_weights: Optional weights for ensemble/stacking (normalized when used).
        use_validation_for_stacking: If True, fit stacking weights on validation when files exist.

    Returns:
        Path to the written submission CSV.
    """
    root = Path(data_root)
    if not root.exists():
        raise FileNotFoundError(f"data_root does not exist: {root}")

    def _run() -> Path:
        test_sequences_path = root / "test_sequences.csv"
        if not test_sequences_path.exists():
            raise FileNotFoundError(f"Missing required file: {test_sequences_path}")

        test_seqs = pd.read_csv(test_sequences_path, usecols=["target_id", "sequence"])
        if max_targets and max_targets > 0:
            test_seqs = test_seqs.head(int(max_targets))

        if model_configs is None:
            resolved_configs: Dict[str, BaselineApproxConfig] = {}
        else:
            resolved_configs = model_configs

        logger.info("Submission strategy: %s", strategy)
        logger.info("  Models: %s", models)
        validate_strategy_models(strategy, models)

        if strategy == "single":
            model_name = models[0]
            config = resolved_configs.get(model_name) or _load_model_config(model_name)
            predictions = _predict_baseline_approx(
                data_root=data_root,
                config=config,
                test_sequences=test_seqs,
            )

        elif strategy == "ensemble":
            predictions_list = []
            for model_name in models:
                config = resolved_configs.get(model_name) or _load_model_config(model_name)
                preds = _predict_baseline_approx(
                    data_root=data_root,
                    config=config,
                    test_sequences=test_seqs,
                )
                predictions_list.append(preds)

            predictions = combine_predictions_weighted_average(
                predictions_list=predictions_list,
                weights=ensemble_weights,
            )

        elif strategy == "stacking":
            predictions_list = []
            for model_name in models:
                config = resolved_configs.get(model_name) or _load_model_config(model_name)
                preds = _predict_baseline_approx(
                    data_root=data_root,
                    config=config,
                    test_sequences=test_seqs,
                )
                predictions_list.append(preds)

            if use_validation_for_stacking:
                validation_labels_path = root / "validation_labels.csv"
                if validation_labels_path.exists():
                    validation_labels = pd.read_csv(validation_labels_path)
                    validation_seqs_path = root / "validation_sequences.csv"
                    if validation_seqs_path.exists():
                        validation_seqs = pd.read_csv(
                            validation_seqs_path, usecols=["target_id", "sequence"]
                        )
                        val_predictions_list = []
                        for model_name in models:
                            config = resolved_configs.get(model_name) or _load_model_config(model_name)
                            val_preds = _predict_baseline_approx(
                                data_root=data_root,
                                config=config,
                                test_sequences=validation_seqs,
                            )
                            val_predictions_list.append(val_preds)

                        stacking_weights = _fit_stacking_weights(
                            predictions_list=val_predictions_list,
                            validation_labels=validation_labels,
                        )
                    else:
                        stacking_weights = None
                else:
                    stacking_weights = None
            else:
                stacking_weights = None

            predictions = combine_predictions_weighted_average(
                predictions_list=predictions_list,
                weights=stacking_weights,
            )

        else:
            raise ValueError(f"Unknown strategy: {strategy}")

        if predictions:
            first_pred = next(iter(predictions.values()))
            n_structures = first_pred.shape[1]
        else:
            n_structures = 5

        out_path = format_predictions_to_submission_csv(
            predictions=predictions,
            sequences_df=test_seqs,
            n_structures=n_structures,
            output_csv=output_csv,
        )

        logger.info("Wrote submission: %s", out_path)
        return out_path

    if validate_first:
        return ValidateFirstRunner(
            validate_fn=validate_rna3d_inputs,
            run_fn=_run,
            data_root=data_root,
            max_targets=0,
        ).run()
    return _run()
