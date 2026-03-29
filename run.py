# ============================================================
# LogIQ — Single Entry Point
# Usage examples:
#
#   python run.py
#   python run.py --model lstm --storage sqlite --pipeline file
#   python run.py --model isolation_forest --storage elasticsearch --pipeline kafka
#   python run.py --backend --storage sqlite
# ============================================================

import argparse
from config.settings import (
    DEFAULT_MODEL, DEFAULT_DATASET,
    DEFAULT_STORAGE, DEFAULT_PIPELINE
)



def run_pipeline(args):
    from datasets.utils      import get_dataset
    from preprocessing.utils import get_preprocessor
    from models.utils        import get_model
    from storage.utils       import get_storage
    from pipeline.utils      import get_pipeline

    print("=" * 60)
    print("LogIQ v2 — AIOps Log Anomaly Detection")
    print("=" * 60)
    print(f"  Dataset  : {args.dataset}")
    print(f"  Model    : {args.model}")
    print(f"  Storage  : {args.storage}")
    print(f"  Pipeline : {args.pipeline}")
    print("=" * 60)

    dataset      = get_dataset(args.dataset)
    preprocessor = get_preprocessor(args.dataset)
    model        = get_model(args.model)
    storage      = get_storage(args.storage)
    pipeline     = get_pipeline(args.pipeline)

    pipeline.run(dataset, preprocessor, model, storage)


def run_backend(args):
    from storage.utils import get_storage
    import backend.app as app_module

    app_module.init_storage(args.storage)
    print(f"[Backend] Starting with storage={args.storage}")
    app_module.app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LogIQ v2")

    parser.add_argument("--model",    default=DEFAULT_MODEL,
                        help="Model to use")
    parser.add_argument("--dataset",  default=DEFAULT_DATASET,
                        help="Dataset to use")
    parser.add_argument("--storage",  default=DEFAULT_STORAGE,
                        help="Storage backend")
    parser.add_argument("--pipeline", default=DEFAULT_PIPELINE,
                        help="Pipeline type")
    parser.add_argument("--backend",  action="store_true",
                        help="Run Flask backend only")

    args = parser.parse_args()

    if args.backend:
        run_backend(args)
    else:
        run_pipeline(args)
