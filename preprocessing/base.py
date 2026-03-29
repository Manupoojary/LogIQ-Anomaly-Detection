# ============================================================
# BasePreprocessor — Every preprocessor must inherit from this
# To add a new preprocessor:
#   1. Create a new file in preprocessing/
#   2. Inherit from BasePreprocessor
#   3. Implement parse() and extract_features()
#   4. Register in preprocessing/utils.py
# ============================================================

import numpy as np


class BasePreprocessor:

    def parse(self, raw_log: str) -> dict:
        """
        Converts raw log string into a structured dictionary.
        Returns None if log cannot be parsed.

        Example output for synthetic:
        {
            "timestamp": "2026-03-21 18:00:00",
            "level":     "ERROR",
            "service":   "AuthService",
            "message":   "Invalid token",
            "user_id":   101
        }
        """
        raise NotImplementedError

    def extract_features(self, parsed_log: dict) -> np.ndarray:
        """
        Converts parsed log dict into a numerical feature vector.
        This is what the ML model receives.
        Must always return the same length array.
        """
        raise NotImplementedError

    def feature_names(self) -> list:
        """
        Returns list of feature names for explainability.
        Must match the order of extract_features() output.
        """
        raise NotImplementedError
