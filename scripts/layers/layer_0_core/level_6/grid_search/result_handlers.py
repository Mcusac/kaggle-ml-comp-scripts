"""Grid search result handlers."""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from level_0 import get_logger
from level_1 import resolve_environment_path
from level_4 import load_json
from level_5 import get_writable_metadata_dir

logger = get_logger(__name__)


def _handle_grid_search_returncode(
    returncode: int,
    stdout_lines: List[str],
    log_file: str,
    error_prefix: str,
) -> None:
    """Raise RuntimeError if returncode is non-zero; otherwise no-op."""
    if returncode != 0:
        error_msg = f"{error_prefix} with return code {returncode}"
        if stdout_lines:
            error_msg += f"\n\nLast {len(stdout_lines)} lines of output:\n" + "\n".join(stdout_lines)
        error_msg += f"\n\nFull output available in: {log_file}"
        raise RuntimeError(error_msg)


def _log_grid_search_success(log_success_fn: Callable[[], None]) -> None:
    """Log success banner, call log_success_fn for search-specific message and details, then banner."""
    logger.info("=" * 60)
    log_success_fn()
    logger.info("=" * 60)


def handle_hyperparameter_grid_search_result(
    returncode: int,
    stdout_lines: List[str],
    log_file: str,
) -> None:
    """
    Handle result from hyperparameter grid search command.

    Raises RuntimeError if returncode is non-zero, otherwise prints success message.

    Args:
        returncode: Process return code
        stdout_lines: Last N lines of stdout output
        log_file: Path to log file (for error messages)

    Raises:
        RuntimeError: If returncode is non-zero
    """
    _handle_grid_search_returncode(
        returncode, stdout_lines, log_file,
        error_prefix="Hyperparameter grid search failed",
    )

    def _log_success():
        logger.info("✅ Hyperparameter grid search complete!")
        logger.info(f"\n📊 Results saved to: {resolve_environment_path('output/hyperparameter_grid_search/')}")
        logger.info("   (All search types append to: gridsearch_results.json)")
        logger.info("   (Already-tested combinations are automatically skipped)")
        logger.info("   Next: Use best hyperparameters for final model training")

    _log_grid_search_success(_log_success)


def handle_dataset_grid_search_result(
    returncode: int,
    stdout_lines: List[str],
    log_file: str,
    dataset_type: Optional[str] = None,
) -> None:
    """
    Handle result from dataset grid search command.

    Raises RuntimeError if returncode is non-zero, otherwise prints success message.

    Args:
        returncode: Process return code
        stdout_lines: Last N lines of stdout output
        log_file: Path to log file (for error messages)
        dataset_type: Dataset type ('full' or 'split')

    Raises:
        RuntimeError: If returncode is non-zero
    """
    _handle_grid_search_returncode(
        returncode, stdout_lines, log_file,
        error_prefix="Grid search failed",
    )

    dataset_type_str = dataset_type or "split"

    def _log_success():
        logger.info("✅ Dataset grid search complete!")
        logger.info(f"\n📊 Results saved to: {resolve_environment_path(f'output/dataset_grid_search_{dataset_type_str}/gridsearch_results.json')}")
        logger.info("   Next: Run Cell 2a (train and export) to train and export the best model")

    _log_grid_search_success(_log_success)


def handle_regression_grid_search_result(
    regression_model_type: str,
    results_file: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Handle regression grid search results and display summary.

    Args:
        regression_model_type: Type of regression model
        results_file: Optional path to results file (auto-detects if None)

    Returns:
        Dictionary with best result information

    Raises:
        FileNotFoundError: If results file not found
    """
    if results_file is None:
        working_dir = get_writable_metadata_dir() / regression_model_type
        results_file = str(working_dir / "gridsearch_metadata.json")

    results_path = Path(results_file)
    if not results_path.exists():
        raise FileNotFoundError(f"Results file not found: {results_file}")

    results = load_json(
        results_path, expected_type=list, file_type="Regression gridsearch metadata JSON"
    )

    successful_results = [r for r in results if r.get("cv_score") is not None]

    if not successful_results:
        logger.warning("No successful results found in regression grid search")
        return {}

    best_result = max(successful_results, key=lambda x: x.get("cv_score", -float("inf")))

    hyperparameters = best_result.get("hyperparameters")
    if not hyperparameters:
        variant_id = best_result.get("variant_id")
        if variant_id:
            try:
                working_dir = get_writable_metadata_dir() / regression_model_type
                metadata_file = working_dir / "metadata.json"
                if metadata_file.exists():
                    variants = load_json(
                        metadata_file, expected_type=list, file_type="Regression metadata JSON"
                    )
                    for variant in variants:
                        if variant.get("variant_id") == variant_id:
                            hyperparameters = variant.get("hyperparameters")
                            if hyperparameters:
                                best_result["hyperparameters"] = hyperparameters
                                break
            except Exception as e:
                logger.warning(f"Failed to retrieve hyperparameters from metadata.json: {e}")

    logger.info("=" * 60)
    logger.info("REGRESSION GRID SEARCH RESULTS")
    logger.info("=" * 60)
    logger.info(f"Total combinations tested: {len(successful_results)}")
    logger.info(f"Best CV Score: {best_result.get('cv_score', 0):.4f}")
    logger.info(f"Best Variant ID: {best_result.get('variant_id', 'unknown')}")
    logger.info(f"Best Hyperparameters: {best_result.get('hyperparameters', {})}")
    logger.info(f"Feature Filename: {best_result.get('feature_filename', 'unknown')}")
    logger.info("=" * 60)

    return best_result
