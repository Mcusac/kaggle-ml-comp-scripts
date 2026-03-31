"""Supervised embedding engine combining PCA, PLS, and GMM into a single feature pipeline."""

import numpy as np

from typing import Optional, Union

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_2 import (
    get_standard_scaler,
    get_pca,
    get_pls_regression,
    get_gaussian_mixture,
)

logger = get_logger(__name__)


class SupervisedEmbeddingEngine:
    """Supervised feature engineering pipeline.

    Combines:
    - StandardScaler: Input normalization.
    - PCA: Unsupervised dimensionality reduction.
    - PLSRegression: Supervised dimensionality reduction (requires targets at fit time).
    - GaussianMixture: Cluster probability features.
    - Optional semantic features: Normalized via a fit-time scaler for consistency.

    All scalers are fitted during fit() and reused during transform(), ensuring
    consistent normalization across train and inference splits.
    """

    def __init__(
        self,
        n_pca: Union[int, float] = 0.80,
        n_pls: int = 8,
        n_gmm: int = 6,
        random_state: int = 42,
    ):
        """Initialize the supervised embedding engine.

        Args:
            n_pca: PCA components. Float in (0, 1) = variance ratio; int = exact components.
            n_pls: Number of PLS components.
            n_gmm: Number of GMM mixture components.
            random_state: Random seed for reproducibility.

        Raises:
            RuntimeError: If scikit-learn is not installed.
        """
        StandardScaler = get_standard_scaler()
        PCA = get_pca()
        PLSRegression = get_pls_regression()
        GaussianMixture = get_gaussian_mixture()

        if StandardScaler is None or PCA is None or PLSRegression is None or GaussianMixture is None:
            raise RuntimeError("sklearn not available. Install with: pip install scikit-learn")

        self.n_pca = n_pca
        self.n_pls = n_pls
        self.n_gmm = n_gmm
        self.random_state = random_state

        self.scaler = StandardScaler()
        self.pca = PCA(n_components=n_pca, random_state=random_state)
        self.pls = PLSRegression(n_components=n_pls, scale=False)
        self.gmm = GaussianMixture(
            n_components=n_gmm,
            covariance_type="diag",
            random_state=random_state,
        )
        self.semantic_scaler = StandardScaler()
        self.pls_fitted_ = False
        self.semantic_fitted_ = False

        logger.info(f"SupervisedEmbeddingEngine initialized: PCA={n_pca}, PLS={n_pls}, GMM={n_gmm}")

    def fit(
        self,
        X: np.ndarray,
        y: Optional[np.ndarray] = None,
        X_semantic: Optional[np.ndarray] = None,
    ) -> "SupervisedEmbeddingEngine":
        """Fit the pipeline on training data.

        Args:
            X: Raw embeddings of shape (N, embedding_dim).
            y: Optional target values of shape (N,) or (N, num_targets) for PLS.
            X_semantic: Optional semantic features of shape (N, num_semantic_features).

        Returns:
            self, for method chaining.
        """
        X_scaled = self.scaler.fit_transform(X)
        self.pca.fit(X_scaled)
        self.gmm.fit(X_scaled)

        if y is not None:
            self.pls.fit(X_scaled, y)
            self.pls_fitted_ = True
            logger.info("PLS regression fitted with target information")
        else:
            logger.info("No targets provided; PLS will be skipped in transform")

        if X_semantic is not None:
            self.semantic_scaler.fit(X_semantic)
            self.semantic_fitted_ = True
            logger.info("Semantic scaler fitted")

        return self

    def transform(
        self,
        X: np.ndarray,
        X_semantic: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        """Transform embeddings using the fitted pipeline.

        Args:
            X: Raw embeddings of shape (N, embedding_dim).
            X_semantic: Optional semantic features of shape (N, num_semantic_features).
                        Must be provided if X_semantic was provided at fit time.

        Returns:
            Engineered feature array of shape (N, num_output_features).
            Output includes PCA components, PLS components (if fitted),
            GMM probabilities, and normalized semantic features (if fitted).
        """
        X_scaled = self.scaler.transform(X)
        features = []

        features.append(self.pca.transform(X_scaled))

        if self.pls_fitted_:
            features.append(self.pls.transform(X_scaled))

        features.append(self.gmm.predict_proba(X_scaled))

        if self.semantic_fitted_:
            if X_semantic is None:
                raise ValueError(
                    "X_semantic was provided at fit time but is missing at transform time."
                )
            features.append(self.semantic_scaler.transform(X_semantic))

        engineered = np.hstack(features)
        logger.debug(f"Transformed: input {X.shape} → output {engineered.shape}")
        return engineered

    def fit_transform(
        self,
        X: np.ndarray,
        y: Optional[np.ndarray] = None,
        X_semantic: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        """Fit and transform in one step.

        Args:
            X: Raw embeddings.
            y: Optional target values.
            X_semantic: Optional semantic features.

        Returns:
            Engineered feature array.
        """
        return self.fit(X, y, X_semantic).transform(X, X_semantic)