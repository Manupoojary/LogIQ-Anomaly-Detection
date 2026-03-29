# ============================================================
# Storage Registry — Add new storage backends here
# Usage: storage = get_storage("sqlite")
# ============================================================

from storage.sqlite        import SQLiteStorage
# from storage.elasticsearch import ElasticsearchStorage

STORAGE_REGISTRY = {
    "sqlite":        SQLiteStorage,
    # "elasticsearch": ElasticsearchStorage,
}


def get_storage(name: str):
    """
    Returns an instance of the requested storage.
    Raises ValueError if storage not found.
    """
    if name not in STORAGE_REGISTRY:
        raise ValueError(
            f"Unknown storage: '{name}'. "
            f"Available: {list(STORAGE_REGISTRY.keys())}"
        )
    return STORAGE_REGISTRY[name]()


def list_storages():
    """Returns list of available storage names."""
    return list(STORAGE_REGISTRY.keys())
