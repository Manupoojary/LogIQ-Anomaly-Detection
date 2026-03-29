# ============================================================
# Dataset Registry — Add new datasets here
# Usage: dataset = get_dataset("synthetic")
# ============================================================

from datasets.synthetic import SyntheticDataset
from datasets.nasa      import NASADataset

DATASET_REGISTRY = {
    "synthetic": SyntheticDataset,
    "nasa":      NASADataset,
}


def get_dataset(name: str):
    """
    Returns an instance of the requested dataset.
    Raises ValueError if dataset not found.
    """
    if name not in DATASET_REGISTRY:
        raise ValueError(
            f"Unknown dataset: '{name}'. "
            f"Available: {list(DATASET_REGISTRY.keys())}"
        )
    return DATASET_REGISTRY[name]()


def list_datasets():
    """Returns list of available dataset names."""
    return list(DATASET_REGISTRY.keys())


