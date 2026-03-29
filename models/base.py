# ============================================================
# BaseModel — Every model must inherit from this
# To add a new model:
#   1. Create a new file in models/
#   2. Inherit from BaseModel
#   3. Implement train(), predict(), is_ready()
#   4. Register in models/utils.py
# ============================================================

import numpy as np

class BaseModel:

    def train(self, X: list):
        """
        Trains the model on a list of feature vectors.
        Called once enough logs are collected.
        """
        raise NotImplementedError

    def predict(self, features: np.ndarray) -> bool:
        """
        Returns True if log is anomalous, False if normal.
        Called for every incoming log.
        """
        raise NotImplementedError

    def is_ready(self) -> bool:
        """
        Returns True if model is trained and ready to predict.
        """
        raise NotImplementedError

    def name(self) -> str:
        """
        Returns model name e.g. "isolation_forest"
        """
        raise NotImplementedError

    def description(self) -> str:
        """
        Human readable description of this model.
        """
        raise NotImplementedError
