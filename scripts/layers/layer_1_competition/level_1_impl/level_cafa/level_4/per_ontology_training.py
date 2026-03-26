"""Per-ontology training workflow for CAFA 6.

This module provides CAFA-specific training workflows that train models
separately for each ontology (F, P, C) with per-ontology hyperparameters.
"""

import time

from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing import cpu_count

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_1 import cleanup_gpu_memory, OntologyConfigResolver

from layers.layer_1_competition.level_1_impl.level_cafa.level_0 import (
    CAFA_ONTOLOGIES,
    OntologyDataLoader,
    OntologyModelManager,
)
from layers.layer_1_competition.level_1_impl.level_cafa.level_3 import OntologyDataPreparer

logger = get_logger(__name__)


class PerOntologyTrainWorkflow:
    """
    Workflow for training models per-ontology with separate hyperparameters.

    This is a CAFA-specific workflow that trains separate models for each
    ontology (F, P, C) with ontology-specific hyperparameters.

    Supports sequential training with GPU cleanup, parallel training,
    and various model loading modes (train_new, load_only, load_or_train).
    """

    def __init__(
        self,
        config,
        contest=None,
        *,
        paths_factory=None,
        config_factory=None,
        data_schema_factory=None,
    ):
        """
        Initialize per-ontology training workflow.

        Args:
            config: Training configuration with per-ontology hyperparameters
            contest: CAFA contest instance (for paths, config, data_schema).
                     If provided, used to obtain paths_factory, config_factory, data_schema_factory.
            paths_factory: Callable returning contest paths (used when contest is None)
            config_factory: Callable(ontology: str) returning contest config (used when contest is None)
            data_schema_factory: Callable returning data schema (used when contest is None)
        """
        self.config = config
        self.ontologies = list(CAFA_ONTOLOGIES)

        if contest is not None:
            self._paths_factory = contest['paths']
            self._config_factory = lambda ont: contest['config'](ontology=ont)
            self._data_schema_factory = contest['data_schema']
        else:
            if paths_factory is None or config_factory is None or data_schema_factory is None:
                raise ValueError(
                    "Either contest or (paths_factory, config_factory, data_schema_factory) required"
                )
            self._paths_factory = paths_factory
            self._config_factory = config_factory
            self._data_schema_factory = data_schema_factory

        self.data_loader = OntologyDataLoader()
        self.data_preparer = OntologyDataPreparer()
        self.model_manager = OntologyModelManager()
        self.config_helper = OntologyConfigResolver()

    def run_train_all(self, sequential: bool = True) -> Dict[str, Any]:
        """
        Train models for all ontologies.

        Trains models for all ontologies (F, P, C) sequentially with
        GPU cleanup between ontologies to prevent memory overflow.

        Args:
            sequential: If True, train sequentially with GPU cleanup between ontologies.
                       If False, train in parallel (requires sufficient resources).

        Returns:
            Dictionary mapping ontology -> training results

        Notes:
            - Per-ontology hyperparameters critical (different optimal params per ontology)
            - GPU cleanup between ontologies prevents memory overflow
            - Sequential training recommended for limited GPU memory
        """
        logger.info("Starting per-ontology training for all ontologies...")
        start_time = time.time()

        results = {}

        if sequential:
            # Sequential training with GPU cleanup
            for ont_code in self.ontologies:
                logger.info(f"Training {ont_code} ontology...")
                ont_start = time.time()

                try:
                    result = self.run_train_single_ontology(ont_code)
                    results[ont_code] = result
                    ont_time = time.time() - ont_start
                    logger.info(f"✓ {ont_code} training complete: {ont_time:.1f}s")
                except Exception as e:
                    logger.error(f"❌ {ont_code} training failed: {e}")
                    results[ont_code] = {'success': False, 'error': str(e)}

                # GPU cleanup between ontologies
                if ont_code != self.ontologies[-1]:  # Don't cleanup after last
                    cleanup_gpu_memory()
                    logger.debug("GPU memory cleaned up after ontology")
        else:
            # Parallel training
            results = self.run_train_parallel_ontologies(self.ontologies)

        total_time = time.time() - start_time
        logger.info(f"Per-ontology training complete: {total_time:.1f}s")
        logger.info(f"Trained {len([r for r in results.values() if r.get('success', False)])} ontologies")

        return results

    def run_train_single_ontology(self, ontology: str) -> Dict[str, Any]:
        """
        Train model for a single ontology.

        Trains a model for one ontology with ontology-specific hyperparameters.
        Uses per-ontology config to get optimal hyperparameters for that ontology.

        Args:
            ontology: Ontology code ('F', 'P', or 'C')

        Returns:
            Training results dictionary with keys:
            - 'success': bool
            - 'ontology': str
            - 'model': trained model or model path
            - 'metrics': dict of training metrics
            - 'time': float (training time in seconds)

        Notes:
            - Per-ontology hyperparameters from config
            - Model loading modes: train_new, load_only, load_or_train
        """
        if ontology not in self.ontologies:
            raise ValueError(f"Invalid ontology: {ontology}. Must be one of {self.ontologies}")

        logger.info(f"Training {ontology} ontology model...")
        start_time = time.time()

        # Get per-ontology hyperparameters
        ontology_config = self.config_helper.get_ontology_config(ontology, self.config)

        # Get contest paths and data schema
        paths = self._paths_factory() if callable(self._paths_factory) else self._paths_factory
        data_schema = self._data_schema_factory() if callable(self._data_schema_factory) else self._data_schema_factory

        # Load training data for this ontology
        logger.info(f"Loading training data for {ontology} ontology...")
        train_data = self.data_loader.load_training_data(ontology, paths, data_schema)

        if train_data is None or len(train_data) == 0:
            logger.warning(f"No training data found for {ontology} ontology")
            return {
                'success': False,
                'ontology': ontology,
                'model': None,
                'metrics': {},
                'time': time.time() - start_time,
                'error': 'No training data available'
            }

        # Prepare features and targets
        X_train, y_train = self.data_preparer.prepare_training_data(
            train_data, ontology, ontology_config
        )

        if X_train is None or X_train.shape[0] == 0:
            logger.warning(f"No valid training samples for {ontology} ontology")
            return {
                'success': False,
                'ontology': ontology,
                'model': None,
                'metrics': {},
                'time': time.time() - start_time,
                'error': 'No valid training samples'
            }

        logger.info(f"Training data: {X_train.shape[0]} samples, {X_train.shape[1]} features, {y_train.shape[1]} targets")

        # Create model with ontology-specific hyperparameters
        model = self.model_manager.create_model(
            ontology, ontology_config, X_train.shape[1], y_train.shape[1]
        )

        # Train model
        logger.info(f"Training {ontology} model...")
        training_metrics = self.model_manager.train_model(model, X_train, y_train, ontology_config)

        # Save model
        model_path = self.model_manager.save_model(model, ontology, paths)

        # Cleanup
        del X_train, y_train, model
        cleanup_gpu_memory()

        result = {
            'success': True,
            'ontology': ontology,
            'model': str(model_path),
            'metrics': training_metrics,
            'time': time.time() - start_time
        }

        logger.info(f"✓ {ontology} training complete: {result['time']:.1f}s")

        return result

    def run_train_parallel_ontologies(self, ontologies: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Train models for multiple ontologies in parallel.

        Trains multiple ontologies in parallel using ThreadPoolExecutor.
        Allows better resource utilization when sufficient GPU memory is available.

        Args:
            ontologies: List of ontology codes to train (default: all ['F', 'P', 'C'])

        Returns:
            Dictionary mapping ontology -> training results

        Notes:
            - Parallel training allows better resource utilization
            - Requires sufficient GPU memory for multiple models
            - Each ontology trains independently
        """
        if ontologies is None:
            ontologies = self.ontologies

        logger.info(f"Starting parallel training for {len(ontologies)} ontologies...")
        start_time = time.time()

        max_workers = min(len(ontologies), cpu_count())
        logger.info(f"Using {max_workers} workers for parallel training")

        results = {}

        def train_ontology_worker(ont_code: str) -> tuple:
            """Worker function for parallel training."""
            try:
                logger.info(f"[Parallel] Starting {ont_code}...")
                result = self.run_train_single_ontology(ont_code)
                logger.info(f"[Parallel] ✓ Completed {ont_code}")
                return (ont_code, result)
            except Exception as e:
                logger.error(f"[Parallel] ❌ Error training {ont_code}: {e}")
                return (ont_code, {'success': False, 'error': str(e)})

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_ont = {
                executor.submit(train_ontology_worker, ont_code): ont_code
                for ont_code in ontologies
            }

            # Collect results as they complete
            for future in as_completed(future_to_ont):
                ont_code = future_to_ont[future]
                try:
                    result_ont_code, result = future.result()
                    results[result_ont_code] = result
                except Exception as e:
                    logger.error(f"{ont_code} training failed: {e}")
                    results[ont_code] = {'success': False, 'error': str(e)}

        total_time = time.time() - start_time
        logger.info(f"Parallel training complete: {total_time:.1f}s")
        logger.info(f"Trained {len([r for r in results.values() if r.get('success', False)])} ontologies")

        return results
