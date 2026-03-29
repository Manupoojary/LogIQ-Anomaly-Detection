# ============================================================
# Preprocessor Registry — Add new preprocessors here
# Usage: preprocessor = get_preprocessor("synthetic")
# ============================================================

from preprocessing.synthetic import SyntheticPreprocessor
from preprocessing.nasa      import NASAPreprocessor

PREPROCESSOR_REGISTRY = {
    "synthetic": SyntheticPreprocessor,
    "nasa":      NASAPreprocessor,
}


def get_preprocessor(dataset_name: str):
    """
    Returns preprocessor matching the dataset name.
    Each dataset has exactly one preprocessor.
    """
    if dataset_name not in PREPROCESSOR_REGISTRY:
        raise ValueError(
            f"No preprocessor for dataset: '{dataset_name}'. "
            f"Available: {list(PREPROCESSOR_REGISTRY.keys())}"
        )
    return PREPROCESSOR_REGISTRY[dataset_name]()


def list_preprocessors():
    """Returns list of available preprocessor names."""
    return list(PREPROCESSOR_REGISTRY.keys())
