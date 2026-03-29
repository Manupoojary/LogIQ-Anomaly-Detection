# ============================================================
# IsolationForestModel — Unsupervised anomaly detection
# Trains on first N logs, then flags outliers
# ============================================================

import numpy as np
from sklearn.ensemble import IsolationForest
from models.base import BaseModel
from config.settings import (
    IF_N_ESTIMATORS,
    IF_CONTAMINATION,
    IF_RANDOM_STATE,
    IF_TRAIN_SIZE
)


class IsolationForestModel(BaseModel):

    def __init__(self):
        self._model = IsolationForest(
            n_estimators  = IF_N_ESTIMATORS,
            contamination = IF_CONTAMINATION,
            random_state  = IF_RANDOM_STATE
        )
        self._trained      = False
        self._train_buffer = []
        self._train_size   = IF_TRAIN_SIZE

    def train(self, X: list):
        """Trains on provided feature vectors."""
        X = np.array(X, dtype=float)
        self._model.fit(X)
        self._trained = True
        print(f"[IsolationForest] Trained on {len(X)} samples")

    def predict(self, features: np.ndarray) -> bool:
        """
        Buffers features until train_size reached,
        then trains and predicts.
        Returns True = anomaly, False = normal.
        """
        self._train_buffer.append(features)

        if not self._trained and len(self._train_buffer) >= self._train_size:
            self.train(self._train_buffer)

        if not self._trained:
            return False

        features = np.array(features, dtype=float).reshape(1, -1)
        prediction = self._model.predict(features)[0]
        return prediction == -1

    def is_ready(self) -> bool:
        return self._trained

    def name(self) -> str:
        return "isolation_forest"

    def description(self) -> str:
        return (
            "Unsupervised anomaly detection using Isolation Forest. "
            f"Trains on first {self._train_size} logs. "
            "No labelled data required."
        )
    
    def reset(self):
        self.model = None
        self.trained = False
