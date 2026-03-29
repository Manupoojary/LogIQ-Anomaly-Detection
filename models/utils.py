# ============================================================
# Model Registry — Add new models here
# Usage: model = get_model("isolation_forest")
# ============================================================

from models.isolation_forest import IsolationForestModel
from models.lstm             import LSTMModel

MODEL_REGISTRY = {
    "isolation_forest": IsolationForestModel,
    "lstm":             LSTMModel,
}


def get_model(name: str):
    """
    Returns a fresh instance of the requested model.
    Raises ValueError if model not found.
    """
    if name not in MODEL_REGISTRY:
        raise ValueError(
            f"Unknown model: '{name}'. "
            f"Available: {list(MODEL_REGISTRY.keys())}"
        )
    return MODEL_REGISTRY[name]()


def list_models():
    """Returns list of available model names."""
    return list(MODEL_REGISTRY.keys())
