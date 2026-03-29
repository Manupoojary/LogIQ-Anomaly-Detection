# ============================================================
# Pipeline Registry — Add new pipelines here
# Usage: pipeline = get_pipeline("file")
# ============================================================

from pipeline.file  import FilePipeline
from pipeline.kafka import KafkaPipeline

PIPELINE_REGISTRY = {
    "file":  FilePipeline,
    "kafka": KafkaPipeline,
}


def get_pipeline(name: str):
    """
    Returns an instance of the requested pipeline.
    Raises ValueError if pipeline not found.
    """
    if name not in PIPELINE_REGISTRY:
        raise ValueError(
            f"Unknown pipeline: '{name}'. "
            f"Available: {list(PIPELINE_REGISTRY.keys())}"
        )
    return PIPELINE_REGISTRY[name]()


def list_pipelines():
    """Returns list of available pipeline names."""
    return list(PIPELINE_REGISTRY.keys())
