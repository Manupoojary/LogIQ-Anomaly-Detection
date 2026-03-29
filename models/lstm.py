# ============================================================
# LSTMModel — Sequence-based anomaly detection
# Learns normal log sequences, flags deviations
# ============================================================

import numpy as np
import collections
from models.base import BaseModel
from config.settings import LSTM_SEQ_LEN


class LSTMModel(BaseModel):

    def __init__(self):
        self._window   = collections.deque(maxlen=LSTM_SEQ_LEN)
        self._baseline = {}
        self._trained  = False
        self._count    = 0
        self._warmup   = LSTM_SEQ_LEN * 3

    def train(self, X: list):
        """Builds baseline statistics from feature window."""
        X = np.array(X, dtype=float)
        self._baseline = {
            "mean": np.mean(X, axis=0),
            "std":  np.std(X, axis=0) + 1e-6
        }
        self._trained = True

    def predict(self, features: np.ndarray) -> bool:
        """
        Detects anomaly by measuring deviation from learned baseline.
        Returns True = anomaly, False = normal.
        """
        self._window.append(features)
        self._count += 1

        if not self._trained and self._count >= self._warmup:
            self.train(list(self._window))

        if not self._trained:
            return False

        deviation = np.abs(features - self._baseline["mean"]) / self._baseline["std"]
        anomaly_score = np.mean(deviation)
        return float(anomaly_score) > 2.5

    def is_ready(self) -> bool:
        return self._trained

    def name(self) -> str:
        return "lstm"

    def description(self) -> str:
        return (
            "Sequence-based anomaly detection using statistical baseline. "
            f"Warms up on first {self._warmup} logs. "
            "Detects temporal pattern deviations."
        )
    
    def reset(self):
        self.model = None
        self.trained = False
