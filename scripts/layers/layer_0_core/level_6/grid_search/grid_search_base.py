"""Base grid search class. Composes components for config, execution, results, and variant building."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from level_0 import ensure_dir, get_logger
from level_1 import BasePipeline, execute_variants
from level_5 import (
    load_results,
    save_results,
    load_checkpoint,
    save_checkpoint,
)

logger = get_logger(__name__)


def _filter_param_grid(
    grid_config: Dict[str, Any],
    quick_mode: bool = False,
    ontology: Optional[str] = None,
    model_type: Optional[str] = None,
) -> Dict[str, List]:
    """
    Filter/resolve parameter grid from config. Returns grid_config as-is.
    Subclasses or contest layer may override with ontology/quick_mode logic.
    """
    del quick_mode, ontology, model_type
    return grid_config if isinstance(grid_config, dict) else {}


class GridSearchBase(BasePipeline, ABC):
    """
    Abstract base class for grid search pipelines.

    Provides common infrastructure for:
    - Variant grid generation
    - Result tracking and saving
    - Checkpoint management
    - Progress tracking
    - Resumability

    Subclasses should implement:
    - `_generate_variant_grid()`: Generate the grid of variants to test
    - `_run_variant()`: Execute a single variant
    - `_create_variant_key()`: Create unique key for variant tracking

    Framework-level grid search base class with support for:
    - Per-ontology parameter grids (contest-specific)
    - Quick mode (smaller parameter space)
    - Checkpoint/resume functionality
    """

    def __init__(
        self,
        config: Any,
        grid_search_type: str,
        results_filename: str = "results.json",
        quick_mode: bool = False,
        ontology: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize grid search base.

        Args:
            config: Configuration object with grid_search settings.
            grid_search_type: Type identifier for this grid search (e.g., 'hyperparameter').
            results_filename: Filename for results JSON (default: 'results.json').
            quick_mode: If True, use smaller parameter grid for faster iteration (default: False).
            ontology: Optional ontology code ('F', 'P', 'C') for per-ontology grids.
            **kwargs: Additional grid search parameters.
        """
        super().__init__(config, **kwargs)
        self.grid_search_type = grid_search_type
        self.results_filename = results_filename
        self.quick_mode = quick_mode
        self.ontology = ontology
        self.results_file: Optional[Path] = None
        self.grid_search_dir: Optional[Path] = None
        self.checkpoint_dir: Optional[Path] = None
        self.completed_variants: Set[Any] = set()
        self.skipped_variants: Set[Any] = set()
        self.results: List[Dict[str, Any]] = []
        self.best_score = -float("inf")
        self.best_variant = None
        self.param_grid: Optional[Dict[str, List]] = None

    def setup(self) -> None:
        """Setup grid search pipeline."""
        logger.info("Setting up grid search pipeline...")
        if not hasattr(self.config, "paths") or not getattr(
            self.config.paths, "output_dir", None
        ):
            raise ValueError(
                "config.paths.output_dir is required for grid search"
            )

        grid_search_name = f"{self.grid_search_type}_grid_search"
        self.grid_search_dir = Path(self.config.paths.output_dir) / grid_search_name
        ensure_dir(self.grid_search_dir)
        self.results_file = self.grid_search_dir / self.results_filename
        self.checkpoint_dir = self.grid_search_dir / "checkpoints"
        ensure_dir(self.checkpoint_dir)

        loaded = self._load_checkpoint()
        if loaded:
            logger.info("Checkpoint loaded successfully")
        elif self.results_file.exists():
            logger.info(f"Loading existing results from {self.results_file}")
            self._load_results()

        if self.quick_mode:
            logger.info("Quick mode enabled: using smaller parameter grid")
        logger.info(f"Grid search setup complete. Directory: {self.grid_search_dir}")

    def execute(self) -> Dict[str, Any]:
        """
        Execute grid search via GridSearchExecutor.
        Returns summary dict: success, total_variants, completed_variants, failed_variants, best_score, best_variant, results.
        """
        logger.info("Starting grid search...")
        variants = self._generate_variant_grid()
        best_score_ref = [self.best_score]
        best_variant_ref = [self.best_variant]

        summary = execute_variants(
            variants=variants,
            run_variant_fn=self._run_variant,
            create_key_fn=self._create_variant_key,
            completed_variants=self.completed_variants,
            results=self.results,
            best_score_ref=best_score_ref,
            best_variant_ref=best_variant_ref,
            save_results_fn=self._save_results,
            save_checkpoint_fn=self._save_checkpoint,
            score_key="score",
        )
        self.best_score = best_score_ref[0]
        self.best_variant = best_variant_ref[0]
        self.skipped_variants = set()
        for r in self.results:
            if r.get("success") is False and r.get("variant_key") is not None:
                self.skipped_variants.add(r["variant_key"])
        return summary

    def get_param_grid(
        self,
        grid_config: Dict[str, Any],
        model_type: Optional[str] = None,
    ) -> Dict[str, List]:
        """Get parameter grid with per-ontology and quick mode support."""
        return _filter_param_grid(
            grid_config,
            quick_mode=self.quick_mode,
            ontology=self.ontology,
            model_type=model_type,
        )

    @abstractmethod
    def _generate_variant_grid(self) -> List[Any]:
        """
        Generate the grid of variants to test.

        Returns:
            List of variants (format depends on subclass).
        """
        ...

    @abstractmethod
    def _create_variant_key(self, variant: Any) -> Any:
        """
        Create unique key for variant tracking.

        Args:
            variant: Variant from the grid.

        Returns:
            Hashable key for tracking this variant.
        """
        ...

    @abstractmethod
    def _run_variant(self, variant: Any, variant_index: int) -> Dict[str, Any]:
        """
        Execute a single variant.

        Args:
            variant: Variant to run (format depends on subclass).
            variant_index: Index of variant in grid.

        Returns:
            Dictionary with variant results:
            - 'success': bool
            - 'score': float (primary metric)
            - 'metrics': dict (additional metrics)
            - 'variant': dict (variant parameters)
        """
        ...

    def _load_results(self) -> None:
        """Load existing results from file."""
        (
            self.results,
            self.best_score,
            self.best_variant,
            self.completed_variants,
        ) = load_results(self.results_file)

    def _save_results(self) -> None:
        """Save results to file."""
        total = len(self._generate_variant_grid())
        save_results(
            self.results_file,
            self.grid_search_type,
            total,
            len(self.completed_variants),
            self.best_score,
            self.best_variant,
            self.results,
        )

    def _save_checkpoint(self) -> None:
        """Save checkpoint."""
        param_grid = self.param_grid if self.param_grid is not None else {}
        total = (
            len(self._generate_variant_grid())
            if hasattr(self, "_generate_variant_grid")
            else 0
        )
        save_checkpoint(
            self.checkpoint_dir,
            self.grid_search_type,
            param_grid,
            self.results,
            self.best_variant,
            self.best_score,
            self.completed_variants,
            total,
            self.quick_mode,
        )

    def _load_checkpoint(self) -> bool:
        """Load checkpoint. Returns True if loaded."""
        out = load_checkpoint(
            self.checkpoint_dir,
            param_grid=self.param_grid,
        )
        if out is None:
            return False
        (
            self.results,
            self.best_score,
            self.best_variant,
            self.completed_variants,
        ) = out
        return True

    def cleanup(self) -> None:
        """Cleanup grid search resources."""
        if self.results_file:
            self._save_results()

        logger.info("Grid search cleanup complete")
